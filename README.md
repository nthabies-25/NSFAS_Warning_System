# NSFAS Warning System — Cloud Edition

A cloud-based student risk assessment system that identifies NSFAS-funded students who may be at risk of academic failure or funding loss. Built on AWS, it ingests academic performance data, computes risk scores, stores results in a managed database, alerts stakeholders when risk thresholds are crossed, and surfaces trends through an interactive dashboard.

> **Note on data:** This project uses **synthetic data only**. No real student records are used. Synthetic data is generated to resemble NSFAS-style academic and funding records for demonstration purposes.

---

## Why this project exists

NSFAS (National Student Financial Aid Scheme) funds thousands of South African students every year, but funding is conditional on academic performance. Students who fall behind can lose funding — often without early warning. This project explores how a cloud data pipeline could flag at-risk students early enough for intervention, using StatsSA-style local context and AWS-native services.

This is a portfolio project built to demonstrate practical cloud computing and data engineering skills: ingestion, serverless processing, managed storage, orchestration, alerting, and visualization — using AWS's free tier / AWS Educate credits wherever possible.

---

## Architecture overview

```
Synthetic CSV data
        │
        ▼
   S3 (raw zone)
        │  triggers
        ▼
  AWS Lambda (risk scoring)
        │
        ▼
   S3 (processed zone) ──► RDS (PostgreSQL)
                                 │
                    ┌────────────┴────────────┐
                    ▼                          ▼
              SNS (alerts)              Streamlit dashboard
                                          (EC2 / Elastic Beanstalk)

        EventBridge schedules the Lambda to re-run periodically
```

**Services used:**
| Service | Role |
|---|---|
| Amazon S3 | Raw and processed data storage |
| AWS Lambda | Serverless risk-scoring logic |
| Amazon RDS (PostgreSQL) | Structured storage for risk records |
| Amazon EventBridge | Scheduled re-scoring runs |
| Amazon SNS | Threshold-crossing alerts |
| Streamlit (on EC2/Elastic Beanstalk) | Interactive dashboard |
| IAM | Least-privilege access control between services |

---

## Risk model

Risk scores are calculated from a small set of weighted academic indicators. Example starting model (adjust as you refine it):

| Factor | Weight | Description |
|---|---|---|
| Module pass rate | 35% | Proportion of enrolled modules passed |
| Attendance | 20% | Recorded attendance percentage |
| Credits completed vs. required | 25% | Progress toward year credit target |
| Repeat modules | 20% | Number of modules being repeated |

Scores are bucketed into **Low / Medium / High** risk. Students in the High bucket trigger an SNS alert.

> This model is intentionally simple to start — it's meant to be explainable, not a black box. You can iterate on weights once you have synthetic data to test against.

---

## Project structure

```
nsfas-warning-system/
├── data/
│   └── generate_synthetic_data.py   # creates synthetic student records
├── lambda/
│   └── risk_scoring.py              # Lambda handler: scoring logic
├── dashboard/
│   └── app.py                       # Streamlit dashboard
├── sql/
│   └── schema.sql                   # RDS table definitions
├── infra/
│   └── (IAM policies, notes on resources created)
└── README.md
```

---

## Getting started

### Prerequisites
- Python 3.10+
- An AWS account (AWS Educate or free tier is fine)
- AWS CLI configured with a non-root IAM user
- `pip install boto3 pandas faker streamlit psycopg2-binary`

### 1. Generate synthetic data
```bash
python data/generate_synthetic_data.py
```
This produces a CSV of synthetic student records (ID, modules, marks, attendance, credits, funding year).

### 2. Set up AWS resources
- Create two S3 buckets: `nsfas-raw-<yourname>` and `nsfas-processed-<yourname>`
- Create an IAM role for Lambda with S3 read/write and RDS connect permissions (least privilege — avoid `*` wildcards)
- Provision an RDS PostgreSQL instance (free-tier eligible `db.t3.micro` is fine) and run `sql/schema.sql` against it

### 3. Deploy the Lambda function
- Package `lambda/risk_scoring.py` with its dependencies
- Set an S3 trigger on the `raw` bucket so new uploads invoke the function
- Test by uploading your synthetic CSV to the raw bucket and checking the processed bucket / RDS table

### 4. Schedule recurring runs
- Create an EventBridge rule to invoke the Lambda on a schedule (e.g. daily at 02:00)

### 5. Set up alerting
- Create an SNS topic (e.g. `nsfas-risk-alerts`)
- Subscribe an email address to it
- Have the Lambda publish to this topic when a student's score crosses the High risk threshold

### 6. Run the dashboard
```bash
streamlit run dashboard/app.py
```
For a hosted version, deploy to EC2 or Elastic Beanstalk and point it at your RDS instance.

---

## Cost management

All services used here have AWS free-tier or AWS Educate credit coverage at small scale. To avoid surprise charges:
- Stop/delete the RDS instance and EC2 instance when not actively developing
- Set a billing alarm in AWS Budgets
- Keep the synthetic dataset small (hundreds, not millions, of rows) during development

---

## Roadmap / possible extensions
- Replace the weighted-average risk model with a simple ML classifier once you have more synthetic history to train on
- Add a QuickSight dashboard as an alternative to Streamlit
- Add authentication to the dashboard (e.g. Cognito) if this moves beyond a personal portfolio piece
- Explore anonymization/POPIA-aligned design patterns in case this is ever adapted for real data

---

## Disclaimer
This is an educational/portfolio project. It does not use, store, or process real NSFAS or student data, and it is not affiliated with or endorsed by NSFAS.

WTC-CBHZRGG5