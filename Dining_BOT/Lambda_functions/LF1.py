import boto3
from datetime import datetime, timedelta


def validate_slot_values(slots):
    response = {}    

    if slots['Location'] is None:
        print("Value for location is not entered yet!")
        response['isValid'] = False
        response['slotViolated'] = 'Location'
        response['message'] = 'I need a few details. Can you tell me the location where you want to search?'
        return slots, response
    else:
        try:
            location_value = slots['Location']['value']['interpretedValue']
            valid_locations = ['manhattan', 'bronx', 'queens', 'brooklyn', 'staten island']
            found = False
            for location in valid_locations:
                if location_value.lower().find(location) != -1:
                    found = True
                    slots['Location']['value']['interpretedValue'] = location
                    break
            
            if not found:
                response['isValid'] = False
                response['slotViolated'] = 'Location'
                response['message'] = 'Uh oh! The location you mentioned is not available, kindly enter the location again.'   
                return slots, response
        except:
            response['isValid'] = False
            response['slotViolated'] = 'Location'
            response['message'] = 'The location you mentioned is not valid, kindly enter the location again.'
            return slots, response

        

    if slots['Cuisine'] is None:
        print("Value for cuisine is not entered yet!")
        response['isValid'] = False
        response['slotViolated'] = 'Cuisine'
        response['message'] = f"{slots['Location']['value']['interpretedValue']}, good choice. What Cuisine would you like to try?"
        return slots, response
    else:
        try:
            cuisine_value = slots['Cuisine']['value']['interpretedValue']
            valid_cuisines = ['american', 'italian', 'chinese', 'japanese', 'mexican', 'french', 
                        'indian', 'thai', 'greek', 'middle eastern', 'korean', 'vegan', 'seafood']
            found = False
            for cuisine in valid_cuisines:
                if cuisine_value.lower().find(cuisine) != -1:
                    found = True
                    slots['Cuisine']['value']['interpretedValue'] = cuisine
                    break
            
            if not found:
                response['isValid'] = False
                response['slotViolated'] = 'Cuisine'
                response['message'] = 'Uh oh! The cuisine you mentioned is not available, kindly enter the cuisine again.'   
                return slots, response
        except:
            response['isValid'] = False
            response['slotViolated'] = 'Cuisine'
            response['message'] = 'The cuisine you mentioned is not valid, kindly enter the cuisine again.'
            return slots, response

    if slots['DiningDate'] is None:
        print("Value for date is not entered yet!")
        response['isValid'] = False
        response['slotViolated'] = 'DiningDate'
        response['message'] = f"{slots['Cuisine']['value']['interpretedValue']} is a great choice. On what date are you looking to make a reservation?"
        return slots, response
    else:
        try:
            diningdate_value = slots['DiningDate']['value']['interpretedValue']
            entered_value = datetime.strptime(diningdate_value, "%Y-%m-%d").date()
            present = datetime.now() + timedelta(hours=-4)
            
            if entered_value < present.date():
                print("Value for date is not correct!")
                response['isValid'] = False
                response['slotViolated'] = 'DiningDate'
                response['message'] = f'Sorry, the date you mentioned {entered_value} has already passed, kindly enter the date again.'
                return slots, response
        except:
            response['isValid'] = False
            response['slotViolated'] = 'DiningDate'
            response['message'] = f'The date you mentioned is not valid, kindly enter the date again.'
            return slots, response
        

    if slots['DiningTime'] is None:
        print("Value for time is not entered yet!")
        response['isValid'] = False
        response['slotViolated'] = 'DiningTime'
        response['message'] = f"What time on {slots['DiningDate']['value']['interpretedValue']} are you looking to make a reservation?"
        return slots, response
    else:
        try:
            diningtime_value = slots['DiningTime']['value']['interpretedValue']
            datetime_value = f"{diningdate_value} {diningtime_value}"
            entered_value = datetime.strptime(datetime_value, "%Y-%m-%d %H:%M")
            present = datetime.now() + timedelta(hours=-4)
            
            if entered_value < present:
                print("Value for time is not correct!")
                response['isValid'] = False
                response['slotViolated'] = 'DiningTime'
                response['message'] = f'Sorry, the time you mentioned {diningtime_value} on the date {diningdate_value} has already passed, kindly enter the time again.'
                return slots, response
        except:
            response['isValid'] = False
            response['slotViolated'] = 'DiningTime'
            response['message'] = 'The time you mentioned is not valid, kindly enter the time again.'
            return slots, response
        

    if slots['NumberOfPeople'] is None:
        print("Value for number of people is not entered yet!")
        response['isValid'] = False
        response['slotViolated'] = 'NumberOfPeople'
        response['message'] = 'Just a few more questions to go. How many people are expected to be there?'
        return slots, response
    else:
        try:
            numberofpeople = int(slots['NumberOfPeople']['value']['interpretedValue'])
            if numberofpeople <= 0:
                print("Value for number of people is not correct!")
                response['isValid'] = False
                response['slotViolated'] = 'NumberOfPeople'
                response['message'] = 'Sorry, the number you entered is not correct, kindly enter the number again.'
                return slots, response
        except:
            response['isValid'] = False
            response['slotViolated'] = 'NumberOfPeople'
            response['message'] = 'The number you mentioned is not valid, kindly enter the number again.'
            return slots, response
        
    if slots['Email'] is None:
        print("Value for email is not entered yet!")
        response['isValid'] = False
        response['slotViolated'] = 'Email'
        response['message'] = 'Please provide me your email ID so that I can send you the reservation details.'
        return slots, response
    else:
        try:
            email_id = slots['Email']['value']['interpretedValue']
        except:
            response['isValid'] = False
            response['slotViolated'] = 'Email'
            response['message'] = 'Sorry, the email you mentioned is not valid, kindly enter the email again.'
            return slots, response
    
    if slots['Confirm'] is None:
        print("Value for confirmation is not entered yet!")
        response['isValid'] = False
        response['slotViolated'] = 'Confirm'
        response['message'] = f"Do you want to confirm the following details(Yes/No)?\n \
            Location: {location_value}\n \
            Cuisine: {cuisine_value}\n \
            Date: {diningdate_value}\n \
            Time: {diningtime_value}\n \
            Number of people: {numberofpeople}\n \
            Email: {email_id}"
        return slots, response
    else:
        try:
            confirmation = slots['Confirm']['value']['interpretedValue']
            if confirmation != 'Yes' and confirmation != 'No':
                response['isValid'] = False
                response['slotViolated'] = 'Confirm'
                response['message'] = f"I'm sorry, I am not able to understand what you said.\n \
                    Do you want to confirm the following details(Yes/No)?\n \
                    Location: {location_value}\n \
                    Cuisine: {cuisine_value}\n \
                    Date: {diningdate_value}\n \
                    Time: {diningtime_value}\n \
                    Number of people: {numberofpeople}\n \
                    Email: {email_id}"
                return slots, response
        except:
            response['isValid'] = False
            response['slotViolated'] = 'Confirm'
            response['message'] = f"I'm sorry, I am not able to understand what you said.\n \
                Do you want to confirm the following details(Yes/No)?\n \
                Location: {location_value}\n \
                Cuisine: {cuisine_value}\n \
                Date: {diningdate_value}\n \
                Time: {diningtime_value}\n \
                Number of people: {numberofpeople}\n \
                Email: {email_id}"
            return slots, response

    response['isValid'] = True
    return slots, response

def sqs_message_sender(slots, sessionID):
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/541457746749/DiningQueue'

    msg_attributes = {}
    for k in slots.keys():
        msg_attributes[k] = {
            'DataType': 'String',
            'StringValue': slots[k]['value']['interpretedValue']
        }

    msg_attributes['sessionID'] = {
        'DataType': 'String',
        'StringValue': sessionID
    }

    response = sqs.send_message(
        QueueUrl = queue_url,
        MessageAttributes = msg_attributes,
        MessageBody = ('User entered information is being sent.')
    )

    print(response['MessageId'])
    print("Message sent to SQS correctly!")
    return


def lambda_handler(event, context):
    print(event)

    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']
    resp = {}
    resp['statusCode'] = 200
    resp['sessionState'] = event['sessionState']

    if event['invocationSource'] == 'DialogCodeHook':
        slots, validate_slots = validate_slot_values(slots)
        if not validate_slots['isValid']:
            resp['sessionState']['dialogAction'] = {
                'type': 'ElicitSlot', 
                'slotToElicit': validate_slots['slotViolated']
            }
            resp['sessionState']['intent'] = {
                'name': intent,
                'slots': slots
            }

            if 'message' in validate_slots:
                mult_messages = validate_slots['message'].splitlines()
                all_messages = []
                for msg in mult_messages:
                    all_messages.append({
                        'contentType': 'PlainText',
                        'content': msg
                    })
                
                resp['messages'] = all_messages

            # print(resp)
            return resp
        else:   # check for the confirmation and reset values if needed
            resp['sessionState']['intent'] = {
                'name': intent,
                'slots': slots
            }

            confirmation = slots['Confirm']['value']['interpretedValue']

            if confirmation == 'No':
                print('Confirmation denied. Please try again.')

                for k in resp['sessionState']['intent']['slots'].keys():
                    resp['sessionState']['intent']['slots'][k] = None

                resp['sessionState']['dialogAction'] = {
                    'type': 'ElicitSlot', 
                    'slotToElicit': 'Location'
                }
                resp['messages'] = [{
                    'contentType': 'PlainText',
                    'content': 'Alright! Please re-enter the details correctly from the beginning!'

                },
                {
                    'contentType': 'PlainText',
                    'content': 'Can you tell me the location where you want to search?'
                }]
            else:
                resp['sessionState']['dialogAction'] = {
                    'type': 'Delegate'
                }
            
            # print(resp)
            return resp

    if event['invocationSource'] == 'FulfillmentCodeHook': 
        resp['sessionState']['dialogAction'] = {
            'type': 'Close'
        }
        resp['sessionState']['intent'] = {
            'name': intent,
            'slots': slots,
            'state':'Fulfilled'
        }
        resp['messages'] = [{
            'contentType': 'PlainText',
            'content': 'Great. The registration details will be sent to your email shortly.'
        }]

        sqs_message_sender(slots, event['sessionId'])   
    
    return resp
