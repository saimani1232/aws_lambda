# SecureShield AI - Main Terraform Configuration
# Deploys the complete serverless security honeypot infrastructure

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "secureshield-terraform-state"
    key    = "secureshield-ai/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "SecureShield AI"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# VPC and Networking
module "vpc" {
  source = "./modules/vpc"
  
  vpc_name           = "secure-shield-vpc"
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  public_subnets     = var.public_subnets
  private_subnets    = var.private_subnets
}

# Security Groups
module "security_groups" {
  source = "./modules/security_groups"
  
  vpc_id = module.vpc.vpc_id
  
  depends_on = [module.vpc]
}

# DynamoDB Tables
module "dynamodb" {
  source = "./modules/dynamodb"
  
  environment = var.environment
}

# Lambda Functions
module "lambda_functions" {
  source = "./modules/lambda"
  
  environment           = var.environment
  vpc_id               = module.vpc.vpc_id
  subnet_ids           = module.vpc.private_subnet_ids
  security_group_ids   = [module.security_groups.lambda_security_group_id]
  threat_intel_table   = module.dynamodb.threat_intel_table_name
  attacker_profiles_table = module.dynamodb.attacker_profiles_table_name
  
  depends_on = [module.dynamodb, module.security_groups]
}

# EventBridge Rules
module "eventbridge" {
  source = "./modules/eventbridge"
  
  environment = var.environment
  
  threat_detector_lambda_arn = module.lambda_functions.threat_detector_lambda_arn
  incident_response_lambda_arn = module.lambda_functions.incident_response_lambda_arn
  intel_collector_lambda_arn = module.lambda_functions.intel_collector_lambda_arn
  alert_dispatcher_lambda_arn = module.lambda_functions.alert_dispatcher_lambda_arn
  honeypot_manager_lambda_arn = module.lambda_functions.honeypot_manager_lambda_arn
  
  depends_on = [module.lambda_functions]
}

# WAF and Security
module "waf" {
  source = "./modules/waf"
  
  environment = var.environment
}

# CloudWatch Dashboards
module "monitoring" {
  source = "./modules/monitoring"
  
  environment = var.environment
}

# Honeypot Infrastructure
module "honeypots" {
  source = "./modules/honeypots"
  
  environment = var.environment
  vpc_id = module.vpc.vpc_id
  subnet_ids = module.vpc.public_subnet_ids
  security_group_ids = [module.security_groups.honeypot_security_group_id]
  
  depends_on = [module.vpc, module.security_groups]
}

# IAM Roles and Policies
module "iam" {
  source = "./modules/iam"
  
  environment = var.environment
  lambda_role_arns = [
    module.lambda_functions.threat_detector_lambda_role_arn,
    module.lambda_functions.incident_response_lambda_role_arn,
    module.lambda_functions.intel_collector_lambda_role_arn,
    module.lambda_functions.alert_dispatcher_lambda_role_arn,
    module.lambda_functions.honeypot_manager_lambda_role_arn
  ]
}

# Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "threat_detector_lambda_arn" {
  description = "Threat Detector Lambda ARN"
  value       = module.lambda_functions.threat_detector_lambda_arn
}

output "threat_intel_table_name" {
  description = "Threat Intelligence DynamoDB Table Name"
  value       = module.dynamodb.threat_intel_table_name
}

output "waf_web_acl_arn" {
  description = "WAF Web ACL ARN"
  value       = module.waf.web_acl_arn
}

output "honeypot_dashboard_url" {
  description = "Honeypot Dashboard URL"
  value       = module.monitoring.dashboard_url
} 