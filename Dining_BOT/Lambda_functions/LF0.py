import boto3
import json

# Define the client to interact with Lex
client = boto3.client('lexv2-runtime')

def lambda_handler(event, context):

    # msg_from_user = event['messages'][0]
    print(event)
    print(context)
    msg_from_user = event['messages'][0]['unstructured']['text']

    # change this to the message that user submits on 
    # your website using the 'event' variable
    # msg_from_user = "Hello"

    print(f"Message from frontend: {msg_from_user}")

    # Initiate conversation with Lex
    response = client.recognize_text(
            botId='TXPGIDFUDQ', # MODIFY HERE
            botAliasId='NUBTECELJV', # MODIFY HERE
            localeId='en_US',
            sessionId='testuser',
            text=msg_from_user)
    
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

        resp = {
            'statusCode': 200,
            'messages': messages
        }

        # modify resp to send back the next question Lex would ask from the user
        
        # format resp in a way that is understood by the frontend
        # HINT: refer to function insertMessage() in chat.js that you uploaded
        # to the S3 bucket

        return resp

