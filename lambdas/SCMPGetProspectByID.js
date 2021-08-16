const AWS = require('aws-sdk');
// const s3 = new AWS.S3();
// const bucket = process.env['s3_bucket'];
var dynamodb = new AWS.DynamoDB();

exports.handler = async function(event, context) {
    if FSO (
        dynamodb = ???.resource('dynamodb') &&
        ProspectID = ??? &&
        table = dynamodb.Table()
        response = table.get_item(Key={'ProspectID': ProspectID})
        response = response['Item']
    ) {
        return {
            'statusCode': 200,
            'body': response
        }
    }
    const response = {
        statusCode: 200,
        body: JSON.stringify('Hello from Lambda!'),
    };
    return response;
    
};



/////////////////// example


var AWS = require("aws-sdk");

AWS.config.update({
  region: "us-west-2",
  endpoint: "http://localhost:8000"
});

var docClient = new AWS.DynamoDB.DocumentClient();

var table = "Movies";

var year = 2015;
var title = "The Big New Movie";

var params = {
    TableName: table,
    Key:{
        "year": year,
        "title": title
    }
};

docClient.get(params, function(err, data) {
    if (err) {
        console.error("Unable to read item. Error JSON:", JSON.stringify(err, null, 2));
    } else {
        console.log("GetItem succeeded:", JSON.stringify(data, null, 2));
    }
});