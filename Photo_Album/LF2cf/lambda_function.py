import json
import logging
import boto3
import requests
from requests_aws4auth import AWS4Auth


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
client = boto3.client('lexv2-runtime')


"""
(1) Identify_intent with LEX
(2) query labels from elastic_search
(3) general Lambda Handler
"""

def print_dict_recursive(d, parent_keys="", indent=0):
    for key, value in d.items():
        current_key = f"{parent_keys}[{key}]" if parent_keys else key
        if isinstance(value, dict):
            print("  " * indent + f"{current_key}:")
            print_dict_recursive(value, current_key, indent + 1)
        else:
            print("  " * indent + f"{current_key}: {value}")

def lambda_handler(event, context):
    print('event : ', event, context)
    
    query = event["queryStringParameters"]['q']
    
    labels = get_labels_from_lex(query)
    img_paths = None
    if len(labels)>0:
        img_paths = find_photo_paths(labels)
        
    if img_paths is None or len(img_paths)==0:
        print("Sending 200 statusCode")
        return{
            'statusCode':200,
            "headers": {"Access-Control-Allow-Origin":"*"},
            'body': json.dumps('No Results found')
        }
    else:
        print("Sending complete List")
        response = {
            'statusCode': 200,
            'headers': {
                
                "Access-Control-Allow-Origin":"*",
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'imagePaths':img_paths,
                'userQuery':query,
                'labels': labels,
            }),
            'isBase64Encoded': False
        }
        
        print(response)
        return response
    
    
def get_labels_from_lex(query):
    
    BOT_ID = "LJGCOGG2PT"
    BOT_ALIAS_ID = "DG4979SPPU"
    
    response = client.recognize_text(
        botId = BOT_ID, # MODIFY HERE
        botAliasId = BOT_ALIAS_ID, # MODIFY HERE
        localeId='en_US',
        sessionId = 'sessionID3',
        text = query)
    
    print_dict_recursive(response['interpretations'][0])
    labels = []
    
    for item in response['interpretations']:
        for key, value in item['intent']['slots'].items():
            if value is not None:
                labels.append(value['value']['interpretedValue'])
                
    return labels
    
def build_es_query(objectKey):
    """
    Build the Elasticsearch query based on the objectKey.
    
    """
    query = {
        "size": 20,
        "query": {
            "query_string": {
                "default_field": "labels",
                "query": f"*{objectKey}*"
            }
        }
    }
    return query
 
def find_photo_paths(key_list):
    
    S3_BUCKET_NAME = "b2store"
    s3 = boto3.client('s3')
    
    
    region = 'us-east-1' # e.g. us-west-1
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    # photos-cf domain endpoint
    host = "https://search-photos-cf-cf6u7zrblae3zhw6fbujdhjm24.us-east-1.es.amazonaws.com"
    index = "photos"
    datatype = "_search"
    url = f'{host}/{index}/{datatype}'
    header = { "Content-Type": "application/json" }
    image_paths = []
    
    for objectKey in key_list:
        query = build_es_query(objectKey)
        response = requests.post(url, auth=awsauth, headers=header, data=json.dumps(query))
        try:
            res = response.json()
            print(res)
            no_of_hits = res['hits']['total']
            hits = res['hits']['hits']
            for hit in hits:
                image_url = s3.generate_presigned_url('get_object', Params={'Bucket':S3_BUCKET_NAME, 'Key':hit["_source"]["objectKey"]})
                image_paths.append(image_url)
        except Exception as e:
            print(f"An error occurred. {e}")
        
    return image_paths