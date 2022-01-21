import os
import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError

region = os.environ['AWS_REGION']
originationNumber = os.environ['ORIGINATION_NUMBER']
application_id = os.environ['APPLICATION_ID']
statemachine_arn = os.environ['STATEMACHINE_ARN']
table_name = os.environ['DYNAMODB_INCIDENTINFO']
table_name_mid = os.environ['DYNAMODB_MESSAGEID']

dynamodbendpointurl = "https://dynamodb." + region + ".amazonaws.com"
dynamodb = boto3.resource('dynamodb', endpoint_url=dynamodbendpointurl)
table_mid = dynamodb.Table(table_name_mid)
table = dynamodb.Table(table_name)

clientpinp = boto3.client('pinpoint')
client_step = boto3.client('stepfunctions')

today = datetime.now()
timestamp = today.strftime("%d/%m/%Y %H:%M:%S")

#Get incident id using message_id from DynamoDB
def get_incident_id(prev_message_id):
    incident_id = table_mid.get_item(Key={'message_id': prev_message_id})
    print("Message_id obtained from DynamoDB using message_id: ")
    print(incident_id)
    incident_id = incident_id['Item']['incident_id']
    return incident_id

#Get incident information from DynamoDB
def get_incident_info(incident_id):
    incident_info = table.get_item(Key={'incident_id': incident_id})
    print("Incident information obtained from DynamoDB: ")
    print(incident_info)
    return incident_info

#Update incident status date in DynamoDB
def update_status_date(incident_id):
    response = table.update_item(
        Key={
            'incident_id': incident_id,
        },
        UpdateExpression="set stat_date = :stat_date",
        ExpressionAttributeValues={
            ':stat_date': timestamp
        },
        ReturnValues="UPDATED_NEW"   
    ) 
    print("Incident status date updated: ")
    print(response)

#Update incident to indicate that there is a double escalation in DynamoDB
def update_escalation_status(incident_id,escalation_status):
    response = table.update_item(
        Key={
            'incident_id': incident_id,
        },
        UpdateExpression="set double_escalation = :double_escalation",
        ExpressionAttributeValues={
            ':double_escalation': escalation_status
        },
        ReturnValues="UPDATED_NEW"   
    )
    print("Incident status updated to indicate double scalation: ")
    print(response)

#Update incident status in DynamoDB
def update_status(incident_id,new_status):
    response = table.update_item(
        Key={
            'incident_id': incident_id,
        },
        UpdateExpression="set incident_stat = :incident_stat",
        ExpressionAttributeValues={
            ':incident_stat': new_status
        },
        ReturnValues="UPDATED_NEW"   
    )
    print("Incident status update: ")
    print(response)

#Delete message_id & incident_id from DynamoDB
def delete_message_id(message_id):
    response = table_mid.delete_item(
        Key={
            'message_id': message_id
        })
    print("Deleted message_id & incident_id from DynamoDB: ")
    print(response)

#Send SMS
def sendsms(destinationNumber, message):

    try:
        send_sms = clientpinp.send_messages(
            ApplicationId=application_id,
            MessageRequest={
                'Addresses': {
                    destinationNumber: {
                        'ChannelType': 'SMS'
                    }
                },
                'MessageConfiguration': {
                    'SMSMessage': {
                        'Body': message,
                        'MessageType': "TRANSACTIONAL",
                        'OriginationNumber': originationNumber
                    }
                }
            }
        )

    except ClientError as e:
        print(e.send_sms['Error']['Message'])
    else:
        message_id = send_sms['MessageResponse']['Result'][destinationNumber]['MessageId']
                
    return message_id
    
#Execute StateMachine
def execute_step_function(data_to_step):
    data_to_step = json.dumps(data_to_step)
    start_step_functions = client_step.start_execution(
        stateMachineArn=statemachine_arn,
        input=data_to_step
        )
    print("StepMachine triggered: ")
    print(start_step_functions)