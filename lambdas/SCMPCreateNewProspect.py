# description:
# HiringMgr adds new prospect via front end form
# triggered via api gateway
# parses info
# publish a new prospect sns noti for send prospect email lambda
# passes response back to front end

import jwt
import json
import boto3
from boto3.dynamodb.conditions import Key
from random import randint
import os

def lambda_handler(event, context):
    
   
    try:
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
    
    
        # parse incoming event, assign variables
        info = event['body']
        ProspectID= str(randint(100000, 999999))
        firstName = info['firstName']
        lastName = info['lastName']
        actionType = info['actionType']
        email = info['email']
        hiringMgr = info['hiringMgr']
        reqClearance = info['reqClearance']
   
        
        
        if MGR or FSO:
            # publish SNS topic 
            message = {
                        'ProspectID': str(ProspectID),
                        'firstName':str(firstName),
                        'lastName':str(lastName),
                        'actionType':str(actionType),
                        'email':str(email),
                        'hiringMgr':str(hiringMgr),
                        'reqClearance':str(reqClearance),
                        'org': str(ID)
                        }
         
            sns = boto3.client('sns')
            response = sns.publish(TargetArn=os.environ['newProspectSNS'],Message=json.dumps({'default': json.dumps(message)}),MessageStructure='json')
      
            
            return{
                'statusCode': 200,
                'body': 'Success'
            }
        else:
            return{
                'statusCode': 400,
                'body': 'Unauthorized'
            }
    except Exception as e:
        return{
            'statusCode': 500,
            'body': 'Internal Server Error'
        }
