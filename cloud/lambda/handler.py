# lambda_function.py
import json
import boto3
import pandas as pd
from io import StringIO
from risk_engine import process_student  # Your engine from Phase 1

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('StudentRisk')

def lambda_handler(event, context):
    """
    Triggered when a CSV is uploaded to the S3 bucket.
    """
    # 1. Parse the S3 event
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        # 2. Download CSV from S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        csv_content = response['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_content))
        
        # 3. Process each student and write to DynamoDB
        with table.batch_writer() as batch:
            for _, row in df.iterrows():
                enriched = process_student(row.to_dict())
                
                # Format for DynamoDB
                item = {
                    'student_id': str(row.get('student_id', 'unknown')),
                    'name': row.get('name', ''),
                    'risk_score': enriched['risk_score'],
                    'risk_level': enriched['risk_level'],
                    'attendance': row.get('attendance', 0),
                    'average_mark': row.get('average_mark', 0)
                }
                batch.put_item(Item=item)
        
        # 4. Audit Log
        print(f"✅ Processed {len(df)} students from {key}")
        
    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete!')
    }