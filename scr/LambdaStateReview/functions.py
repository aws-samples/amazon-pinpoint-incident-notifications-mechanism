import os
import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError

region = os.environ['AWS_REGION']
originationNumber = os.environ['ORIGINATION_NUMBER']
application_id = os.environ['APPLICATION_ID']
table_name = os.environ['DYNAMODB_INCIDENTINFO']
table_name_mid = os.environ['DYNAMODB_MESSAGEID']

dynamodbendpointurl = "https://dynamodb." + region + ".amazonaws.com"
dynamodb = boto3.resource('dynamodb', endpoint_url=dynamodbendpointurl)
table = dynamodb.Table(table_name)
table_mid = dynamodb.Table(table_name_mid)

clientpinp = boto3.client('pinpoint')

today = datetime.now()
timestamp = today.strftime("%d/%m/%Y %H:%M:%S")

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
    print("Update incident status date in DynamoDB: ")
    print(response)

#Get the double escalation status for that incident_id from DynamoDB
def get_double_escalation_status(incident_id):
    status = table.get_item(Key={'incident_id': incident_id})
    print("Get incident status from DynamoDB: ")
    print(status)
    status = status['Item']['double_escalation']
    return status
    
#Get the status for that incident_id from DynamoDB
def get_status(incident_id):
    status = table.get_item(Key={'incident_id': incident_id})
    print("Get incident status from DynamoDB: ")
    print(status)
    status = status['Item']['incident_stat']
    return status

# Delete message_id & incident_id from DynamoDB
def delete_message_id(message_id):
    response = table_mid.delete_item(
        Key={
            'message_id': message_id
        })
    print("Delete message_id & incident_id from DynamoDB: ")
    print(response)

#Update incident status in DynamoDB
def update_incident_stat(incident_id, stat):
    response = table.update_item(
        Key={
            'incident_id': incident_id,
        },
        UpdateExpression="set incident_stat = :incident_stat",
        ExpressionAttributeValues={
            ':incident_stat': stat
        },
        ReturnValues="UPDATED_NEW"   
    )
    print("Update incident status in DynamoDB: ")
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
