# Description:
# FSO updates a prospect record from front end
# Invoke via API Gateway
# Publish SNS topic

import json
import boto3
import os
from boto3.dynamodb.conditions import Key
import jwt

def lambda_handler(event, context):
    
     # get auth token from headers 
    token = event['headers']['Authorization']

    #### Token Validation ####
    
    # decode token (ignore signature)
    decoded = jwt.decode(token,options={"verify_signature": False})
    ID = decoded['identities'][0]['providerName']
    
    # get role values from token
    TokenRoles = decoded['profile']
    TokenAdminRole = decoded['cognito:groups']
    
    # initialize and set role statuses to false
    FSO = False
    MGR = False
    Admin = False
    
    # get roles to validate against
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['attribTable'])
    response = table.query(
        KeyConditionExpression=Key('ID').eq(ID)
    )
    
    responseObject= response['Items'][0]
    MappedFSORole = responseObject['ADFSO']
    MappedMGRRole = responseObject['ADMGR']
    print(responseObject)
    # validate
    if (MappedFSORole in str(TokenRoles)):
        FSO = True
    
    if (MappedMGRRole in str(TokenRoles)):
        MGR = True
    
    if 'Admin' in TokenAdminRole:
        Admin = True
    
    print('fso '+str(FSO))
    print('mgr '+str(MGR))
    print('admin '+str(Admin))
    
    print(event['body'])
    if FSO:
    
        # create variables for prospect info passed from api gateway
        message = json.dumps(event['body'])
    
        # publish SNS topic 
        sns = boto3.client('sns')
        response = sns.publish(
            TargetArn=os.environ['SNSARN'],
            Message=json.dumps({'default': message}),
            MessageStructure='json'
        )
        print(response)
        
        
        
        # TODO implement
        return {
            'statusCode': 200,
            'body': 'Information Updated!'
        }
    else:
        return {
            'statusCode': 400,
            'body': 'Unauthorized'
        }
