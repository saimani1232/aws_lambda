# SecureShield AI - Terraform Variables

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones for the region"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "public_subnets" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "private_subnets" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24", "10.0.12.0/24"]
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 300
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 512
}

variable "bedrock_model_id" {
  description = "AWS Bedrock model ID for AI analysis"
  type        = string
  default     = "anthropic.claude-3-sonnet-20240229-v1:0"
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for alerts"
  type        = string
  default     = ""
  sensitive   = true
}

variable "jira_api_url" {
  description = "JIRA API URL"
  type        = string
  default     = ""
}

variable "jira_api_token" {
  description = "JIRA API token"
  type        = string
  default     = ""
  sensitive   = true
}

variable "pagerduty_api_key" {
  description = "PagerDuty API key"
  type        = string
  default     = ""
  sensitive   = true
}

variable "pagerduty_service_id" {
  description = "PagerDuty service ID"
  type        = string
  default     = ""
}

variable "threat_intel_retention_days" {
  description = "Number of days to retain threat intelligence data"
  type        = number
  default     = 90
}

variable "honeypot_cleanup_hours" {
  description = "Number of hours before honeypot cleanup"
  type        = number
  default     = 24
}

variable "enable_cloudtrail" {
  description = "Enable CloudTrail for event logging"
  type        = bool
  default     = true
}

variable "enable_guardduty" {
  description = "Enable GuardDuty for threat detection"
  type        = bool
  default     = true
}

variable "enable_security_hub" {
  description = "Enable Security Hub for security findings"
  type        = bool
  default     = true
}

variable "waf_rate_limit" {
  description = "WAF rate limit for suspicious IPs"
  type        = number
  default     = 2000
}

variable "waf_block_duration" {
  description = "WAF block duration in minutes"
  type        = number
  default     = 1440  # 24 hours
}

variable "honeypot_types" {
  description = "Types of honeypots to deploy"
  type        = list(string)
  default     = ["web_server", "database", "file_server", "api_endpoint"]
  
  validation {
    condition = alltrue([
      for type in var.honeypot_types : contains(["web_server", "database", "file_server", "api_endpoint"], type)
    ])
    error_message = "Honeypot types must be one of: web_server, database, file_server, api_endpoint."
  }
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
} 