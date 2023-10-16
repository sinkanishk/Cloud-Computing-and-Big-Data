import boto3
import json

# Define the client to interact with Lex
client = boto3.client('lexv2-runtime')

def lambda_handler(event, context):

    # msg_from_user = event['messages'][0]
    print(event)
    msg_from_user = event['messages'][0]['unstructured']['text']
    try:
        sessionID = event['sessionID']
    except:
        sessionID = 'invalid'

    # change this to the message that user submits on 
    # your website using the 'event' variable
    # msg_from_user = "Hello"

    print(f"Message from frontend: {msg_from_user}")

    # Initiate conversation with Lex
    response = client.recognize_text(
            botId='TXPGIDFUDQ', # MODIFY HERE
            botAliasId='NUBTECELJV', # MODIFY HERE
            localeId='en_US',
            sessionId=sessionID,
            text=msg_from_user)
    
    print(response)

    msg_from_lex = response.get('messages', [])
    if msg_from_lex:
        messages = []
        print(f"Messages from Chatbot:")
        for idx in range(len(msg_from_lex)):
            print(f"{idx + 1}. ", msg_from_lex[idx]['content'])
            messages.append({
                'type': 'unstructured',
                'unstructured': {
                    'text': msg_from_lex[idx]['content']
                }
            })

        if response['sessionState']['intent']['name'] == 'GreetingIntent' and sessionID != 'invalid':
            try:
                dynamodb = boto3.resource('dynamodb')
                table = dynamodb.Table('UserRecommendation')
                response = table.get_item(Key={'sessionID': sessionID})
                item = response.get('Item')
                recommend_msg = item.get('recommend', 'No recommendations')
                print(f"Message: {recommend_msg}")
                messages.append({
                    'type': 'unstructured',
                    'unstructured': {
                        'text': 'By the way, here are some recommendations based on your previous search'
                    }
                })
                recommend_msgs = recommend_msg.split('\n')
                for msg in recommend_msgs:
                    messages.append({
                        'type': 'unstructured',
                        'unstructured': {
                            'text': msg
                        }
                    })
            except:
                pass
        
        resp = {
            'statusCode': 200,
            'messages': messages
        }

        # modify resp to send back the next question Lex would ask from the user
        
        # format resp in a way that is understood by the frontend
        # HINT: refer to function insertMessage() in chat.js that you uploaded
        # to the S3 bucket

        return resp
