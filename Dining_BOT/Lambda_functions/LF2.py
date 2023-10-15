import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
from botocore.vendored import requests
from botocore.exceptions import ClientError
from requests_aws4auth import AWS4Auth
import requests


def receive_sqs_message(queue_url):
    sqs = boto3.client("sqs")

    response = sqs.receive_message(
        QueueUrl=queue_url, 
        AttributeNames=['SentTimestamp'],
        MessageAttributeNames=['All'],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    messages = response.get('Messages', [])
    if not messages:
        print("No messages in the queue")
        return None
    message = messages[0]
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=message['ReceiptHandle']
    )
    print('Received and deleted message: %s' % response)
    return message

def create_aws_auth():
    """
    Create AWS authentication using boto3 credentials.
    """
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session(
        aws_access_key_id="", 
        aws_secret_access_key="", 
        region_name="us-east-1"
    ).get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key, 
        credentials.secret_key, 
        region, 
        service, 
        session_token=credentials.token
    )
    return awsauth

def build_es_query(cuisine):
    """
    Build the Elasticsearch query based on the cuisine.
    """
    return {
        "size": 1300,
        "query": {
            "query_string": {
                "default_field": "cuisine",
                "query": cuisine
            }
        }
    }

def find_restaurant_from_elasticsearch(cuisine):
    """
    Search for restaurants in Elasticsearch based on cuisine.
    """
    host = 'search-yelpdata-bsjyud2u3efoaw2cr224ym7avy.us-east-1.es.amazonaws.com'
    index = 'yelpdata'
    url = f'https://{host}/{index}/_search'
    awsauth = create_aws_auth()
    headers = {"Content-Type": "application/json"}
    
    query = build_es_query(cuisine)


    response = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))
    
    try:
        res = response.json()
        no_of_hits = res['hits']['total']
        hits = res['hits']['hits']
    except:
        print("An error occurred.")
        return []

    business_ids = [str(hit['_id']) for hit in hits]
    return business_ids



def retrieve_message_info(message):
    """
    Retrieve relevant information from the SQS message.
    """
    try:
        cuisine = message["MessageAttributes"]["Cuisine"]["StringValue"]
        location = message["MessageAttributes"]["Location"]["StringValue"]
        date = message["MessageAttributes"]["DiningDate"]["StringValue"]
        time = message["MessageAttributes"]["DiningTime"]["StringValue"]
        numOfPeople = message["MessageAttributes"]["NumberOfPeople"]["StringValue"]
        email = message["MessageAttributes"]["Email"]["StringValue"]
        return cuisine, location, date, time, numOfPeople, email
    except KeyError:
        print("Invalid message format. Missing required keys.")
        return None, None, None, None, None, None

def fetch_restaurant_info(business_ids, max_results=5):
    """
    Fetch restaurant information for the given business IDs from DynamoDB.
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('YelpRestaurants')
    restaurant_info = []

    # Iterate through business IDs and retrieve restaurant information
    itr = 1
    for business_id in business_ids:
        if itr > max_results:
            break
        
        response = table.get_item(Key={'bID': business_id})
        item = response.get('Item')
        if item:
            name = item.get("name", "Unknown Restaurant")
            address = item.get("address", "Unknown Address")
            restaurant_info.append({"name": name, "address": address})
            itr += 1

    return restaurant_info

def build_message_to_send(cuisine, location, numOfPeople, date, time, b_IDS):
    """
    Build the message to send based on retrieved information and Elasticsearch results.
    """
    # message_to_send = ascii_art()
    # message_to_send += "\n"
    message_to_send += f'Hello! Here are my {cuisine} restaurant suggestions in {location} for {numOfPeople} people, for {date} at {time}:\n'
    
    # Fetch restaurant information for the given business IDs
    restaurant_info = fetch_restaurant_info(b_IDS, max_results=5)
    
    if restaurant_info:
        for i, info in enumerate(restaurant_info, start=1):
            name = info.get('name', 'Unknown Restaurant')
            address = info.get('address', 'Unknown Address')
            message_to_send += f'{i}. {name}, located at {address}.\n'
    else:
        message_to_send += 'No restaurants found for the provided cuisine.\n'
    
    message_to_send += 'Enjoy your meal!!'
    return message_to_send


def send_email_recommendation(email, message_to_send):
    """
    Send the recommendation email to the user.
    """
    ses_client = boto3.client('ses', region_name='us-east-1')
    
    try:
        response = ses_client.send_email(
            Destination={"ToAddresses": [email]},
            Message={
                'Subject': {'Data': 'Dining Concierge Recommendation'},
                'Body': {'Text': {'Data': message_to_send}}
            },
            Source="ks4038@columbia.edu"
        )
        print("Email sent successfully.")
    except Exception as e:
        print("Error sending email:", str(e))


def lambda_handler(event, context):
    # DEFINE THIS AFTER SETTING UP THE SQS
    queue_url = "https://sqs.us-east-1.amazonaws.com/541457746749/DiningQueue"
    
    while True:
    
        message = receive_sqs_message(queue_url)
        if message is None:
            print("No Message in the Queue right-NOW")
            return
        
        cuisine, location, date, time, numOfPeople, email = retrieve_message_info(message)
        business_ids = find_restaurant_from_elasticsearch(cuisine)
        message_to_send = build_message_to_send(cuisine, location, numOfPeople, date, time, business_ids)
        send_email_recommendation(email, message_to_send)
    
    return message_to_send
    
    
    