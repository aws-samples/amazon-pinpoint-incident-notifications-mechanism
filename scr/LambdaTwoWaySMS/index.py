import json
import boto3
from datetime import datetime
from functions import sendsms, delete_message_id, update_status, get_incident_info, get_incident_id, execute_step_function, update_escalation_status, update_status_date

def lambda_handler(event, context):
    
    records = event['Records']
    
    for record in records:
        message = record['Sns']
        message = message['Message']
        message = json.loads(message)
        print(message)

        prev_message_id = message['previousPublishedMessageId']
        destinationNumber = message['originationNumber']
        message_body = (str(message['messageBody'])).lower()
        
        #Get incident_id from the DynamoDB incident_db_message_id using the previous message id from the SNS payload
        incident_id = get_incident_id(prev_message_id)
        
        #Get data for this incident 
        incident_info = get_incident_info(incident_id)
        
        description = incident_info['Item']['description']
        url = incident_info['Item']['url']
        first_contact = incident_info['Item']['first_contact']
        second_contact = incident_info['Item']['second_contact']
        incident_status = incident_info['Item']['incident_stat']
        
        if message_body == "yes":
            
            #Update incident status to acknowledged and insert the timestamp of the event
            new_status = "acknowledged"
            update_status(incident_id,new_status)
            update_status_date(incident_id)
            
            #Send confirmation SMS that their SMS was received
            message = "Thank you for the confirmation, please follow the link from the previous SMS to resolve the issue"
            new_message_id = sendsms(destinationNumber, message)

            #Delete message id line from DynamoDB
            delete_message_id(prev_message_id)
            delete_message_id(new_message_id)
        
        elif message_body == "no" and incident_status == "escalation":
            
            #Update double_escalation to yes for this incident
            escalation_status = "yes"
            update_escalation_status(incident_id,escalation_status)
            
            #Send SMS to inform that the incident will be escalated
            message = "This incident is already escalated"
            sendsms(destinationNumber, message)            
            
            #Creating StepFunctions Input JSON object
            data_to_step = {
                "incident_id":incident_id,
                "description":description,
                "url":url,
                "first_contact":first_contact,
                "second_contact":second_contact,
                "incident_stat":"double_escalation",
                "skip_to_end" : "yes"
            }
            
            execute_step_function(data_to_step)
        
        elif message_body == "no" and incident_status == "not_acknowledged":
            
            #Send SMS to inform that the incident will be escalated
            message = "The incident will be escalated"
            sendsms(destinationNumber, message)
            
            #Update incident status to escalation
            new_status = "escalation"
            update_status(incident_id,new_status)
            
            #Delete message id line from DynamoDB
            delete_message_id(prev_message_id)
            
            #Creating StepFunctions Input JSON object
            data_to_step = {
                "incident_id":incident_id,
                "description":description,
                "url":url,
                "first_contact":first_contact,
                "second_contact":second_contact,
                "incident_stat":new_status
            }
            
            #Trigger step functions
            execute_step_function(data_to_step)