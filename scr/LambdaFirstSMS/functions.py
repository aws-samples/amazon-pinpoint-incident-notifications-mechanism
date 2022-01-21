import os
import boto3
from botocore.exceptions import ClientError

region = os.environ['AWS_REGION']
originationNumber = os.environ['ORIGINATION_NUMBER']
application_id = os.environ['APPLICATION_ID']
table_name = os.environ['DYNAMODB_MESSAGEID']

client_pinp = boto3.client('pinpoint')
dynamodbendpointurl = "https://dynamodb." + region + ".amazonaws.com"
dynamodb = boto3.resource('dynamodb', endpoint_url=dynamodbendpointurl)
table = dynamodb.Table(table_name)

#Store the message_id & incident_id in DynamoDB
def store_message_id(message_id, incident_id):
    response = table.put_item(
       Item={
            'message_id': message_id,
            'incident_id': incident_id
            }
        )
    print("Message_id & Incident_id added in DynamoDB: ")
    print(response)

#Send SMS
def sendsms(destinationNumber, description, url, sending_status):
    
    message = (""" Hello, this is an INCIDENT SMS \n\n""" + description + """\n\n""" + url + """\n\n Reply YES to acknowledge or NO to decline.\n\n""" +  """Sending status: """ + sending_status)

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