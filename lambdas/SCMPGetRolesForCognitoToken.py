import json

def lambda_handler(event, context):
    print('here is event: '+ str(event))
    # grab requestor's email address
    email = event['request']['userAttributes']['email']
    print('here is email: '+ str(email))
    # placeholder variable
    pet_preference = ''
    
    # set preference to 'dogs' if email contains @amazon.com
    # otherwise preference is 'cats'
    if "@amazon.com" in email:
        pet_preference = 'dogs'
    else:
        pet_preference = 'cats'
    
    event["response"]["claimsOverrideDetails"] = { 
        "claimsToAddOrOverride": { 
            "pet_preference": pet_preference 
            }
        }
        
    return {
        'statusCode': 200,
        'body': event
    }

