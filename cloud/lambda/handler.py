import json
import csv
import io
import os
import boto3
from risk_engine import RiskEngine

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
sns_client = boto3.client('sns')

table = dynamodb.Table('StudentRisk')

# Set this as a Lambda environment variable after you create the SNS topic
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')


def _to_number(value, default=0):
    """CSV values arrive as strings — convert safely, falling back on default."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def lambda_handler(event, context):
    """
    Triggered when a CSV is uploaded to the S3 bucket.
    """
    high_risk_names = []

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # 1. Download CSV from S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        csv_content = response['Body'].read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(csv_content))

        processed_count = 0

        # 2. Process each student and write to DynamoDB
        with table.batch_writer() as batch:
            for row in reader:
                student = {
                    'student_id': row.get('student_id', 'unknown'),
                    'name': row.get('name', ''),
                    'attendance': _to_number(row.get('attendance')),
                    'average_mark': _to_number(row.get('average_mark')),
                    'failed_modules': _to_number(row.get('failed_modules')),
                }

                enriched = RiskEngine.process_student(student)

                item = {
                    'student_id': str(enriched['student_id']),
                    'name': enriched['name'],
                    'risk_score': int(enriched['risk_score']),
                    'risk_level': enriched['risk_level'],
                    'attendance': int(enriched['attendance']),
                    'average_mark': str(enriched['average_mark']),  # DynamoDB Decimal-safe
                }
                batch.put_item(Item=item)
                processed_count += 1

                if enriched['risk_level'] == 'HIGH':
                    high_risk_names.append(f"{enriched['name']} ({enriched['student_id']}) — score {enriched['risk_score']}")

        print(f"Processed {processed_count} students from {key}")

    # 3. Alert on high-risk students, if SNS is configured
    if high_risk_names and SNS_TOPIC_ARN:
        message = "The following students were flagged HIGH risk:\n\n" + "\n".join(high_risk_names)
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="NSFAS Risk Alert: High-risk students flagged",
            Message=message
        )
        print(f"SNS alert sent for {len(high_risk_names)} high-risk students")

    return {
        'statusCode': 200,
        'body': json.dumps(f'Processing complete. {len(high_risk_names)} high-risk students flagged.')
    }
