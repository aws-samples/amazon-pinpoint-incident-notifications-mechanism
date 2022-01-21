import json
from functions import sendsms, store_message_id

def lambda_handler(event, context):
    print(event)
    
    incident_id = event['incident_id']
    description = event['description']
    url = event['url']
    first_contact = event['first_contact']
    second_contact = event['second_contact']
    incident_stat = event['incident_stat']
    
    try:
        auto_escalation = event['auto_escalation']
        print(auto_escalation)
    except:
        auto_escalation = "no"
        print(auto_escalation)
    try:
        skip_to_end = event["skip_to_end"]
    except:
        skip_to_end = "no"
    
    #Check the status of the incident and perform the respective actions
    if incident_stat == "escalation" and skip_to_end == "no":
        sending_status = "escalation"
        message_id = sendsms(second_contact, description, url, sending_status)
        store_message_id(message_id, incident_id)
    
    elif incident_stat == "not_acknowledged":
        sending_status = "normal"
        message_id = sendsms(first_contact, description, url, sending_status)
        store_message_id(message_id, incident_id)
    
    else:
        message_id = "na"
        sending_status = "na"

    return {
        'incident_id': incident_id,
        'description': description,
        'url': url,
        'first_contact': first_contact,
        'second_contact': second_contact,
        'message_id': message_id,
        'sending_status': sending_status,
        'skip_to_end': skip_to_end,
        'incident_stat': incident_stat,
        'auto_escalation': auto_escalation
    }