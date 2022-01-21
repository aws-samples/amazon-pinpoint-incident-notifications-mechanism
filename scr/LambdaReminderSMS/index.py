import json
from functions import get_status, store_message_id, sendsms,  delete_message_id, get_escalation_status

def lambda_handler(event, context):
    print(event)
    
    incident_id = event['incident_id']
    description = event['description']
    url = event['url']
    first_contact = event['first_contact']
    second_contact = event['second_contact']
    sending_status = event['sending_status']
    message_id_first_step = event['message_id']
    
    try:
        auto_escalation = event['auto_escalation']
        print(auto_escalation)
    except:
        auto_escalation = "no"
        print(auto_escalation)
    
    delete_message_id(message_id_first_step) #Delete message id record from the first SMS in DynamoDB
    status = get_status(incident_id) #Get the incident status from
    escalation_status = get_escalation_status(incident_id)
    
    if status == "acknowledged":
        message_id = "na"
        
    elif status == "not_acknowledged" and escalation_status == "no":
        message_id = sendsms(second_contact, description, url, sending_status)
        store_message_id(message_id, incident_id)
        
    elif sending_status == "escalation" and escalation_status == "no":
        message_id = sendsms(second_contact, description, url, sending_status)
        store_message_id(message_id, incident_id)
        
    else:
        message_id = "na"
    
    return {
        'incident_id': incident_id,
        'description': description,
        'url': url,
        'first_contact': first_contact,
        'second_contact': second_contact,
        'message_id': message_id,
        'sending_status': sending_status,
        'incident_stat': status,
        'double_escalation': escalation_status,
        'auto_escalation': auto_escalation
    }