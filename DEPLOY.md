# Fast-track deploy

Run these in order from your project root:
`/Users/nthabiemoloi/Desktop/NSFAS_Warning_System`

Activate your venv first if it isn't already active:
```bash
source venv/bin/activate
```

---

## 0. Configure AWS credentials (do this first — you're currently blocked here)

If you don't yet have an IAM user with access keys:
1. AWS Console → IAM → Users → Create user (e.g. `nthabie-dev`)
2. Attach policies: `AmazonDynamoDBFullAccess`, `AmazonS3ReadOnlyAccess`, `AmazonSNSFullAccess`
   (broader than least-privilege — fine for today's demo, mention this trade-off on camera)
3. Create an access key (use case: "Command Line Interface") — copy the Access Key ID and Secret Access Key, the secret is shown once

Then:
```bash
aws configure
```
Enter your Access Key ID, Secret Access Key, region `af-south-1`, output format `json`.

Verify:
```bash
aws sts get-caller-identity
```
Should print your account ID and user ARN, not an error.

---

## 1. DynamoDB table
```bash
aws dynamodb create-table \
  --table-name StudentRisk \
  --attribute-definitions AttributeName=student_id,AttributeType=S \
  --key-schema AttributeName=student_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region af-south-1
```

Verify it exists:
```bash
aws dynamodb describe-table --table-name StudentRisk --region af-south-1
```

## 2. S3 bucket
```bash
aws s3 mb s3://nsfas-raw-nthabie --region af-south-1
```
(Bucket names are globally unique — if this name is taken, try `nsfas-raw-nthabie-<random digits>`.)

## 3. SNS topic (for high-risk alerts)
```bash
aws sns create-topic --name nsfas-risk-alerts --region af-south-1
```
Copy the returned `TopicArn`, then:
```bash
aws sns subscribe \
  --topic-arn <TopicArn from above> \
  --protocol email \
  --notification-endpoint your-email@example.com \
  --region af-south-1
```
Check your inbox and confirm the subscription before moving on — SNS won't deliver until you do.

## 4. IAM role for Lambda (separate from your personal IAM user in step 0)
Create a role `nsfas-lambda-role` trusted by `lambda.amazonaws.com`, and attach:
- `AWSLambdaBasicExecutionRole`
- `AmazonS3ReadOnlyAccess`
- `AmazonDynamoDBFullAccess`
- `AmazonSNSFullAccess`

(Same today's-deadline trade-off as step 0 — broader than least privilege.)

## 5. Package and deploy the Lambda

Your engine copy should already be in place from earlier
(`cloud/lambda/risk_engine.py`, copied from `src/engine/risk_engine.py`).
Re-sync it if you've edited the source since:
```bash
cp src/engine/risk_engine.py cloud/lambda/risk_engine.py
```

Zip and deploy:
```bash
cd cloud/lambda
zip -r ../../function.zip handler.py risk_engine.py
cd ../..

aws lambda create-function \
  --function-name nsfas-risk-processor \
  --runtime python3.12 \
  --role arn:aws:iam::<account-id>:role/nsfas-lambda-role \
  --handler handler.lambda_handler \
  --zip-file fileb://function.zip \
  --timeout 30 \
  --environment "Variables={SNS_TOPIC_ARN=<TopicArn from step 3>}" \
  --region af-south-1
```
Replace `<account-id>` — find it with `aws sts get-caller-identity`.

## 6. Wire the S3 trigger
```bash
aws lambda add-permission \
  --function-name nsfas-risk-processor \
  --statement-id s3invoke \
  --action "lambda:InvokeFunction" \
  --principal s3.amazonaws.com \
  --source-arn arn:aws:s3:::nsfas-raw-nthabie

aws s3api put-bucket-notification-configuration \
  --bucket nsfas-raw-nthabie \
  --notification-configuration '{
    "LambdaFunctionConfigurations": [{
      "LambdaFunctionArn": "arn:aws:lambda:af-south-1:<account-id>:function:nsfas-risk-processor",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {"Key": {"FilterRules": [{"Name": "suffix", "Value": ".csv"}]}}
    }]
  }'
```

## 7. Test the pipeline
```bash
aws s3 cp data/raw/students.csv s3://nsfas-raw-nthabie/students.csv
```
Check CloudWatch Logs for the Lambda (`nsfas-risk-processor` log group), then:
```bash
aws dynamodb scan --table-name StudentRisk --region af-south-1
```
You should see enriched records. Check your email for the SNS alert if any student scored HIGH.

## 8. Run the dashboard
```bash
python3 -m streamlit run dashboard/app.py
```
(Use `python3 -m streamlit`, not the bare `streamlit` command — this avoids the interpreter mismatch you hit earlier.)

---

# Demo video script (aim for 3–5 min)

1. **Intro (20s):** What the project does and why — NSFAS funding risk, synthetic data, South African context.
2. **Architecture (30s):** Show the diagram from your README — S3 → Lambda → DynamoDB → SNS/Dashboard.
3. **Live upload (60s):** Upload `students.csv` to S3 in the console or CLI, on camera.
4. **Show it work (60s):** Switch to CloudWatch Logs to show the Lambda executing, then DynamoDB table with new records.
5. **Alert (30s):** Show the SNS email for a HIGH risk student.
6. **Dashboard (60s):** Walk through Streamlit — summary metrics, chart, filterable table.
7. **Close (20s):** One sentence on what you'd add next (least-privilege IAM cleanup, EventBridge scheduling, QuickSight).

Record with screen + webcam corner (OBS, QuickTime, or Loom all fine) — a working pipeline on camera matters more than production polish.
