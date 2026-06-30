# main.tf

provider "aws" {
  region = "af-south-1"
}

# S3 Bucket for Data Lake 
resource "aws_s3_bucket" "nsfas_data_lake" {
  bucket = "nsfas-risk-data-${random_id.bucket_suffix.hex}"
  force_destroy = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "nsfas_encrypt" {
  bucket = aws_s3_bucket.nsfas_data_lake.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "nsfas_block_public" {
  bucket = aws_s3_bucket.nsfas_data_lake.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDB for Fast Risk Retrieval (NoSQL)
resource "aws_dynamodb_table" "student_risk" {
  name           = "StudentRisk"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "student_id"
  
  attribute {
    name = "student_id"
    type = "S"
  }

   # Add Global Secondary Index for querying by risk level
  global_secondary_index {
    name            = "RiskLevelIndex"
    hash_key        = "risk_level"
    projection_type = "ALL"
  }
  
  tags = {
    Environment = "NSFAS_Prod"
  }
}

# Random suffix for unique bucket name
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# Output the bucket name for reference
output "s3_bucket_name" {
  value = aws_s3_bucket.nsfas_data_lake.bucket
}

