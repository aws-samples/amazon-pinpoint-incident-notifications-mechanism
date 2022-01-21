from functions import get_status, delete_message_id, update_incident_stat, sendsms, update_status_date, get_double_escalation_status

def lambda_handler(event, context):
    print(event)

    incident_id = event['incident_id']
    description = event['description']
    url = event['url']
    first_contact = event['first_contact']
    second_contact = event['second_contact']
    payload_status = event['incident_stat']
    sending_status = event['sending_status']
    
    try:
        auto_escalation = event['auto_escalation']
        print(auto_escalation)
    except:
        auto_escalation = "no"  
        print(auto_escalation)
    try:
        skip_to_end = event['skip_to_end']
    except:
        skip_to_end = "no"
    try:
        message_id_second = event['message_id']
        delete_message_id(message_id_second)
    except:
        message_id_second ="na"
    
    status = get_status(incident_id)
    double_escalation = get_double_escalation_status(incident_id)
    
    data_to_return = {
            "auto_escalation": "no"
        }
    
    if status == "not_acknowledged" and double_escalation == "no":
        
        #Escelate the incident by updating its status in Dynamo
        stat = "escalation"
        update_incident_stat(incident_id, stat)
        
        #Creating StepFunctions Input JSON object
        #data_to_step
        data_to_return = {
            "incident_id":incident_id,
            "description":description,
            "url":url,
            "first_contact":first_contact,
            "second_contact":second_contact,
            "incident_stat" : "escalation",
            "auto_escalation": "yes"
        }
        
        #trigger_step_function(data_to_step)
        
        #Send SMS to inform that the incident has now been escalated
        message = "The incident has now been escalated"
        sendsms(first_contact, message)
    
    elif skip_to_end == "yes" or payload_status == "double_escalation" or auto_escalation == "yes":
        
        #Send SMS to inform that the incident has been sent to X for review
        message = "The incident was not acknowledged by anyone. It will be logged for review."
        sendsms(second_contact, message)
        
        #Update status and status date
        stat = "not_acknowledged"
        update_incident_stat(incident_id, stat)
        update_status_date(incident_id)
    
    elif sending_status == "escalation" and status == "escalation":
        
        try:
            #Delete message id line from DynamoDB
            delete_message_id(message_id_second)
        except:
            print("No message id to delete")
        
        #Send SMS to inform that the incident has been sent to X for review
        message = "The incident was not acknowledged by anyone. It will be logged for review."
        sendsms(second_contact, message)
        
        #Update status and status date
        stat = "not_acknowledged"
        update_incident_stat(incident_id, stat)
        update_status_date(incident_id)

    return data_to_return