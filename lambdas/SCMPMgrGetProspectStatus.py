import boto3
import json
from boto3.dynamodb.conditions import Key
import os
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
    
    if MGR:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['table'])
        # should be a query rather than scan, probably not good practice to have all 
        # PII data passed back here 
        response = table.scan()
        email = decoded['identities'][0]['userId']
        Prospects = []
        
        for record in response['Items']:
            if email in record['hiringMgr']:
                firstName = record['firstName']
                lastName = record['lastName']
                ID = record['ProspectID']
                actionStatus = record['actionStatus']
                actionType = record['actionType']
                try:
                    statusDate = record['statusDate']
                except Exception as e:
                    statusDate = ''
                prospect = {'firstName':firstName,'lastName':lastName,'type':actionType,'status':actionStatus,'statusDate':statusDate, 'ID':ID}
                Prospects.append(prospect)
        
        
        return {
            'statusCode': 200,
            'body': Prospects
        }
    else:
        return {
            'statusCode': 400,
            'body': 'unauthorized'
        }

