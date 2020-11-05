import json
import boto3

def lambda_handler(event, context):
    
    labels_list = []
    db_image_name = ""
    
    ##  Iterates through the messages recieved and extracts the bucket name and image name from the message body.

    for record in event['Records']:
       payload=record['body']
       message = json.loads(payload)
       bucket_name = message["Records"][0]["s3"]["bucket"]["name"]
       image_name = message["Records"][0]["s3"]["object"]["key"]
       db_image_name = image_name
       
       ##   Sets the rekognition client and sends the image and the bucket which contains it to the rekognition service.
       ##   The response is the retrieved and each label obtained is iterated and added to an array.

       rekog_client = boto3.client('rekognition')
       rekog_response = rekog_client.detect_labels(Image = {"S3Object" : {"Bucket" : bucket_name, "Name" : image_name,}}, MaxLabels=5)
       for label in rekog_response['Labels']:
           print(label)
           labels_list.append(label["Name"])
    

    ##  Sets the dynamodb client and adds a new entry with the image name being the primary key

    dynamoDB_client = boto3.client('dynamodb')
    dynamoDB_client.put_item(TableName='CourseworkImageLabels', Item={'Image_name': {'S':db_image_name}})
    

    ##  Iterates over each index of the array of labels. Then, the newly created dynamodb table is updated with each label 
    ##  retrieved from the dynamodb table by using the 'update_item' function in the boto3 dynamodb client.

    for i, entry in enumerate(labels_list):
        label_key = "Label_"+str(i+1)
        dynamoDB_client.update_item(TableName='CourseworkImageLabels',
            Key={'Image_name': {'S':db_image_name}},
            UpdateExpression="set "+label_key+" = :val1",
            ExpressionAttributeValues={
                ":val1": {'S':entry}
            },
            ReturnValues="UPDATED_NEW"
        )
       
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }