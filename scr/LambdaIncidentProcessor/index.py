import os
import json
import boto3 

statemachine_arn = os.environ['STATEMACHINE_ARN']
client_step = boto3.client('stepfunctions')

def lambda_handler(event, context):
    
    for record in event['Records']:
        print(record)
        
        if record['eventName']=="INSERT":
            try:
                description = record['dynamodb']['NewImage']['description']['S']
            except:
                print("Not a full new record")
            else:
                incident_id = record['dynamodb']['NewImage']['incident_id']['S']
                description = record['dynamodb']['NewImage']['description']['S']
                url = record['dynamodb']['NewImage']['url']['S']
                first_contact = record['dynamodb']['NewImage']['first_contact']['S']
                second_contact = record['dynamodb']['NewImage']['second_contact']['S']
                incident_stat = record['dynamodb']['NewImage']['incident_stat']['S']
                
                #Creating StateMachine input JSON object
                data_to_step = {
                    "incident_id":incident_id,
                    "description":description,
                    "url":url,
                    "first_contact":first_contact,
                    "second_contact":second_contact,
                    "incident_stat": incident_stat
                }
                data_to_step = json.dumps(data_to_step)
                
                #Trigger StateMachine
                start_step_functions = client_step.start_execution(
                    stateMachineArn= statemachine_arn,
                    input=data_to_step
                    )
                print("Trigger StateMachine: ")
                print(start_step_functions)