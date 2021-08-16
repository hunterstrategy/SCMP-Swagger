# Description:
# FSO selects a prospect on front end table to review
# invoked via api gateway
# gets record with matching ProspectID
# returns record

import boto3
import json
import os
import jwt
from boto3.dynamodb.conditions import Key

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
    
    
    if FSO:
        dynamodb = boto3.resource('dynamodb')
        # Parse event for ProspectId
        ProspectID = str(event['body'])
        # query Dynamo for record with same key
        table = dynamodb.Table(os.environ['Table'])
        response = table.get_item(Key={'ProspectID': ProspectID})
        response = response['Item']
        # format results
        # TODO implement
        return {
            'statusCode': 200,
            'body': response
        }
    else:
        return {
            'statusCode': 400,
            'body': 'Unauthorized'
        }

