import os
import boto3
from botocore.exceptions import ClientError

region = os.environ['AWS_REGION']
originationNumber = os.environ['ORIGINATION_NUMBER']
application_id = os.environ['APPLICATION_ID']
table_name = os.environ['DYNAMODB_INCIDENTINFO']
table_name_mid = os.environ['DYNAMODB_MESSAGEID']

client_pinp = boto3.client('pinpoint')
dynamodbendpointurl = "https://dynamodb." + region + ".amazonaws.com"
dynamodb = boto3.resource('dynamodb', endpoint_url=dynamodbendpointurl)
table_mid = dynamodb.Table(table_name_mid)
table = dynamodb.Table(table_name)

# Delete message id from DynamoDB from the first SMS
def delete_message_id(message_id):
    response = table_mid.delete_item(
        Key={
            'message_id': message_id
        })
    print("Delete message_id & incident_id from DynamoDB: ")
    print(response)

#Get the double_escalation status for that incident_id from DynamoDB
def get_escalation_status(incident_id):
    escalation_status = table.get_item(Key={'incident_id': incident_id})
    print("Get escalation status from DynamoDB: ")
    print(escalation_status)
    escalation_status = escalation_status['Item']['double_escalation']
    return escalation_status

#Get the status for that incident_id from DynamoDB
def get_status(incident_id):
    status = table.get_item(Key={'incident_id': incident_id})
    print("Get incident status from DynamoDB: ")
    print(status)
    status = status['Item']['incident_stat']
    return status
    
#Store the message_id & incident_id in DynamoDB
def store_message_id(message_id, incident_id):
    response = table_mid.put_item(
       Item={
            'message_id': message_id,
            'incident_id': incident_id
            }
        )
    print("Insert message_id & incident_id in DynamoDB: ")
    print(response)

#Send SMS
def sendsms(destinationNumber, description, url, sending_status):
    
    message = ("""REMINDER \n\n""" + """Hello, this is an INCIDENT SMS \n\n""" + description + """\n\n""" + url + """\n\n Reply YES to acknowledge or NO to decline.\n\n""" +  """Sending status: """ + sending_status)
    
    try:
        send_sms = client_pinp.send_messages(
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
        print(send_sms)
                
    return message_id