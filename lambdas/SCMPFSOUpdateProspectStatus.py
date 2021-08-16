# Description
# Invoke via UpdateStatus SNS
# Update corresponding prospect's status in dynamo
# Email to notify hiring manager/ HR
# Email to notifiy prospect


import json
import boto3
import os
from boto3.dynamodb.conditions import Key
def lambda_handler(event, context):
    
    # create variable for prospect info passed from SNS
    snsMessage = event['Records'][0]['Sns']['Message']
    # body = json.loads(snsMessage)
    prospectInfo = eval(snsMessage)
    print(prospectInfo)
    
    # update record
    table = boto3.resource('dynamodb').Table(os.environ['tableName'])
    response = table.update_item(
        Key={
            'ProspectID': prospectInfo['ProspectID']
        },
        UpdateExpression="set actionStatus=:a, statusDate=:b",
        ExpressionAttributeValues={
            ':a': prospectInfo['status'],
            ':b': prospectInfo['statusDate']
        },
        ReturnValues="UPDATED_NEW"
    )
    
    # publish SNS for to notify HR/ Manager that record has been updated
    # get roles to validate against
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['tableName'])
    usrResponse = table.query(
        KeyConditionExpression=Key('ProspectID').eq(prospectInfo['ProspectID'])
    )
    
    responseObject= usrResponse['Items'][0]
 
    
    
    # Get required info about hiring manager and prospect
    mgrEmail = responseObject['hiringMgr']
    proEmail = responseObject['busEmail']
    
    
    
    # send mgr email
    CHARSET = "UTF-8"
    BODY_HTML = """<html>
    <head></head>
    <body>
      <h1>Hunter Strategy Security Clearnance Management Portal</h1>
      <h3>One of your prospect's information has been updated, log on to view changes. </h3>
    
    </body>
    </html>"""
    BODY_TEXT=("Hunter Strategy Security Clearnance Management Portal" +"\n"
                +"One of your prospect's information has been updated, log on to view changes.")
    
    client = boto3.client('ses')
    client.send_email(
    Destination={
        'ToAddresses': [mgrEmail],
    },
    Message={
        'Body': {
            'Html': {
                    'Charset': CHARSET,
                    'Data': BODY_HTML,
                },
                'Text': {
                    'Charset': CHARSET,
                    'Data': BODY_TEXT,
                },
            },
        'Subject': {
            'Charset': 'UTF-8',
            'Data': 'Onboarding Portal: Action Required - Prospect Information Updated',
        },
    },
    Source='noreply@portal.hunterstrategy.net',
    )
    
    # send prospect email
    CHARSET = "UTF-8"
    BODY_HTML = """<html>
    <head></head>
    <body>
      <h1>Hunter Strategy Security Clearnance Management Portal</h1>
      <h3>Your information has been reviewed! </h3>
      <h3>Hang tight and expect to hear from your hirining manager shortly with futher details.</h3>
    </body>
    </html>"""
    BODY_TEXT=("Hunter Strategy Security Clearnance Management Portal" +"\n"
                +"Your information has been reviewed! Hang tight and you will hear from your hiring manager shortly.")
    
    client = boto3.client('ses')
    client.send_email(
    Destination={
        'ToAddresses': [proEmail],
    },
    Message={
        'Body': {
            'Html': {
                    'Charset': CHARSET,
                    'Data': BODY_HTML,
                },
                'Text': {
                    'Charset': CHARSET,
                    'Data': BODY_TEXT,
                },
            },
        'Subject': {
            'Charset': 'UTF-8',
            'Data': 'Onboarding Portal: Information Review is Complete',
        },
    },
    Source='noreply@portal.hunterstrategy.net',
    )
    
    
    # respond to front end
    output = str(response['Attributes']['actionStatus'])
    
    
    return {
        'statusCode': 200,
        'body': '"'+output+'"'
    }

