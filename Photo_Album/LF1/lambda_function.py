import boto3
import json
import requests
import logging
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def detect_labels(photo, bucket):
    client = boto3.client('rekognition')

    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
    MaxLabels=10,
    # Uncomment to use image properties and filtration settings
    #Features=["GENERAL_LABELS", "IMAGE_PROPERTIES"],
    #Settings={"GeneralLabels": {"LabelInclusionFilters":["Cat"]},
    # "ImageProperties": {"MaxDominantColors":10}}
    )

    # print('Detected labels for ' + photo)
    # print()
    labels = []
    for label in response['Labels']:
        # print("Label: " + label['Name'], "   Confidence: " + str(label['Confidence']))
        labels.append(label['Name'])
    
    return labels
        

def s3_metadata(photo, bucket):
    s3_client = boto3.client("s3")
    data = s3_client.head_object(Bucket=bucket, Key=photo)
    print(data)
    # extract custom labels if present
    try:
        customLabels = data['ResponseMetadata']['HTTPHeaders']['x-amz-meta-customlabels']
        customLabels = customLabels.split(',')
        for idx, label in enumerate(customLabels):
            label = label.lstrip()
            label = label.rstrip()
            customLabels[idx] = label
    except:
        customLabels = []

    # print(customLabels)
    return customLabels


def upload_to_es(object, id):
    region = 'us-east-1' # e.g. us-west-1
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    host = "search-photos-275s2jekaejxrizkwwlk6um4uq.us-east-1.es.amazonaws.com"
    
    os_client = OpenSearch(hosts=[{ 'host': host, 'port': 443}],
                        http_auth=awsauth, 
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)

    response = os_client.index(
        index="photos",
        body=object,
        id =id,
        refresh=True
    )
    print(response)
    # print("Uploaded labels to OpenSearch successfully")


def lambda_handler(event, context):
    # Triggered when an image is uploaded to the S3 bucket
    try:
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        photo_name = event['Records'][0]['s3']['object']['key']
        # print(bucket_name, photo_name)
        customLabels = s3_metadata(photo_name, bucket_name)
        newLabels = detect_labels(photo_name, bucket_name)
        customLabels.extend(newLabels)
        
        upload_object = {
            "objectKey": photo_name,
            "bucket": bucket_name,
            "createdTimeStamp": datetime.now().replace(microsecond=0).isoformat(),
            "labels": customLabels
        }
        print(json.dumps(upload_object))
        upload_to_es(json.dumps(upload_object), photo_name)
        response = "Uploaded labels to OpenSearch successfully"
    except:
        response = "Issue with uploading image to OpenSearch"

    print(response)
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }