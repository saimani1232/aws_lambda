# SecureShield AI - Complete Execution Guide

## 🎯 Quick Start (5 Minutes)

### Step 1: Verify Prerequisites
```bash
# Check if you have all required software
aws --version
terraform --version
python3 --version
```

### Step 2: Configure AWS
```bash
# Configure AWS credentials
aws configure
# Enter your AWS Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)

# Verify AWS access
aws sts get-caller-identity
```

### Step 3: Deploy the Project
```bash
# Navigate to project directory
cd aws

# Make deployment script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh dev us-east-1
```

### Step 4: Run Demo
```bash
# Run the hackathon demo
python3 scripts/demo.py --demo-type full
```

## 📋 Detailed Step-by-Step Execution

### Phase 1: Environment Setup (10 minutes)

#### 1.1 Install Required Software
```bash
# Install AWS CLI
# Windows: Download from https://aws.amazon.com/cli/
# macOS: brew install awscli
# Linux: sudo apt-get install awscli

# Install Terraform
# Windows: Download from https://www.terraform.io/downloads.html
# macOS: brew install terraform
# Linux: curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -

# Install Python 3.9+
# Windows: Download from https://www.python.org/downloads/
# macOS: brew install python@3.9
# Linux: sudo apt-get install python3 python3-pip python3-venv
```

#### 1.2 Setup Python Environment
```bash
# Navigate to project directory
cd aws

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 1.3 Configure AWS Account
```bash
# 1. Create AWS account at https://aws.amazon.com/
# 2. Create IAM user with programmatic access
# 3. Attach AdministratorAccess policy (for demo)
# 4. Download access keys

# Configure AWS CLI
aws configure
# AWS Access Key ID: [Your Access Key]
# AWS Secret Access Key: [Your Secret Key]
# Default region name: us-east-1
# Default output format: json

# Verify configuration
aws sts get-caller-identity
```

#### 1.4 Enable AWS Bedrock
```bash
# Go to AWS Console → Bedrock
# Click "Get started"
# Request access to Claude models
# Wait for approval (usually instant)
```

### Phase 2: Project Deployment (15 minutes)

#### 2.1 Prepare Deployment
```bash
# Ensure you're in the project directory
cd aws

# Create outputs directory
mkdir -p outputs

# Make scripts executable
chmod +x scripts/deploy.sh
```

#### 2.2 Run Deployment
```bash
# Deploy to development environment
./scripts/deploy.sh dev us-east-1

# The script will:
# 1. Check prerequisites
# 2. Install Python dependencies
# 3. Create S3 bucket for Terraform state
# 4. Deploy infrastructure with Terraform
# 5. Deploy Lambda functions
# 6. Setup monitoring
# 7. Setup honeypots
# 8. Run tests
```

#### 2.3 Monitor Deployment
```bash
# Watch deployment progress
# The script will show detailed output for each step

# Expected output:
# [INFO] Starting SecureShield AI deployment...
# [INFO] Environment: dev
# [INFO] Region: us-east-1
# [SUCCESS] Prerequisites check passed
# [SUCCESS] Dependencies installed
# [SUCCESS] Terraform state bucket created
# [SUCCESS] Infrastructure deployed successfully
# [SUCCESS] Lambda functions deployed
# [SUCCESS] Monitoring setup completed
# [SUCCESS] Honeypot infrastructure setup completed
# [SUCCESS] Tests completed
# [SUCCESS] SecureShield AI deployment completed successfully!
```

### Phase 3: Verification & Testing (10 minutes)

#### 3.1 Verify Infrastructure
```bash
# Check AWS resources
aws lambda list-functions --query 'Functions[?contains(FunctionName, `secure-shield`)].FunctionName'
aws dynamodb list-tables --query 'TableNames[?contains(@, `secure-shield`)]'
aws events list-rules --query 'Rules[?contains(Name, `secure-shield`)].Name'
```

#### 3.2 Test Lambda Functions
```bash
# Test threat detector
aws lambda invoke \
  --function-name secure-shield-threat-detector-dev \
  --payload '{"test": "event"}' \
  response.json

# Check response
cat response.json
```

#### 3.3 Run Unit Tests
```bash
# Run all tests
python3 -m pytest tests/ -v

# Expected output:
# test_threat_detector.py::TestThreatDetector::test_extract_event_details PASSED
# test_threat_detector.py::TestThreatDetector::test_pattern_analysis_reconnaissance PASSED
# ...
```

### Phase 4: Demo Execution (5 minutes)

#### 4.1 Run Full Demo
```bash
# Run complete demo
python3 scripts/demo.py --demo-type full

# Expected output:
# 🚀 SecureShield AI - Live Demo
# ==================================================
# 📊 Step 1: Normal Operations Dashboard
# ✅ Normal activity: admin from 10.0.1.100 - DescribeInstances
# ✅ Normal activity: developer from 10.0.1.101 - ListBuckets
# ✅ Normal activity: analyst from 10.0.1.102 - GetObject
# 📈 All systems operational - No threats detected
# 
# 🔍 Step 2: Reconnaissance Attack Detection
# 🚨 Suspicious activity detected!
# ⚠️  Reconnaissance attempt 1: DescribeInstances from 192.168.1.50
#    Tool detected: nmap/7.80
# ...
```

#### 4.2 Run Quick Demo
```bash
# Run quick demo for time-constrained presentations
python3 scripts/demo.py --demo-type quick
```

#### 4.3 Run Live Attack Simulation
```bash
# Run live attack simulation
python3 scripts/demo.py --demo-type live
```

### Phase 5: Monitoring & Management (Ongoing)

#### 5.1 Access CloudWatch Dashboards
```bash
# Get dashboard URL
aws cloudwatch list-dashboards --query 'DashboardEntries[?contains(DashboardName, `secure-shield`)].DashboardName'

# Open in browser: https://console.aws.amazon.com/cloudwatch/home#dashboards
```

#### 5.2 Monitor Lambda Functions
```bash
# Check Lambda logs
aws logs describe-log-groups --query 'logGroups[?contains(logGroupName, `secure-shield`)].logGroupName'

# View recent logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/secure-shield-threat-detector-dev \
  --start-time $(date -d '1 hour ago' +%s)000
```

#### 5.3 Check Threat Intelligence
```bash
# Query DynamoDB for threat data
aws dynamodb scan \
  --table-name secure-shield-threat-intel-dev \
  --select COUNT
```

## 🎬 Hackathon Presentation Script

### 3-Minute Demo Flow

#### Minute 1: Introduction & Setup (60 seconds)
```bash
# Start with project overview
echo "🔒 SecureShield AI - Automated Cloud Security Honeypot"
echo "AI-powered threat detection with automated response"
echo "Built on AWS serverless architecture"

# Show normal operations
python3 scripts/demo.py --demo-type quick
```

#### Minute 2: Attack Simulation (60 seconds)
```bash
# Simulate attack and show response
echo "🚨 Simulating cyber attack..."
echo "🔍 AI-powered threat detection in action..."
echo "⚡ Automated response execution..."

# Run live simulation
python3 scripts/demo.py --demo-type live
```

#### Minute 3: Results & Intelligence (60 seconds)
```bash
# Show results and business value
echo "📊 Threat intelligence gathered..."
echo "🎣 Adaptive honeypots deployed..."
echo "💰 Business value demonstrated..."

# Show dashboard metrics
python3 scripts/demo.py --demo-type full
```

## 🔧 Troubleshooting

### Common Issues & Solutions

#### Issue 1: AWS Credentials Not Configured
```bash
# Error: Unable to locate credentials
# Solution:
aws configure
# Enter your AWS access keys
```

#### Issue 2: Terraform State Lock
```bash
# Error: Error acquiring the state lock
# Solution:
terraform force-unlock [LOCK_ID]
# Or delete the lock file in S3
```

#### Issue 3: Lambda Function Errors
```bash
# Check Lambda logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/secure-shield-threat-detector-dev \
  --start-time $(date -d '10 minutes ago' +%s)000
```

#### Issue 4: Bedrock Access Denied
```bash
# Error: AccessDeniedException
# Solution:
# 1. Go to AWS Console → Bedrock
# 2. Request access to Claude models
# 3. Wait for approval
```

#### Issue 5: External Service Errors
```bash
# For Slack/JIRA/PagerDuty errors
# These are optional - the system works without them
# Set empty values in .env file:
SLACK_WEBHOOK_URL=""
JIRA_API_TOKEN=""
PAGERDUTY_API_KEY=""
```

## 📊 Performance Monitoring

### Key Metrics to Monitor
```bash
# Threat detection rate
aws cloudwatch get-metric-statistics \
  --namespace "SecureShield/ThreatDetection" \
  --metric-name "ThreatsDetected" \
  --start-time $(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Response time
aws cloudwatch get-metric-statistics \
  --namespace "SecureShield/IncidentResponse" \
  --metric-name "ResponseTime" \
  --start-time $(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

## 🧹 Cleanup (When Done)

### Remove All Resources
```bash
# Navigate to terraform directory
cd terraform

# Destroy infrastructure
terraform destroy -auto-approve

# Remove S3 bucket (if empty)
aws s3 rb s3://secureshield-terraform-state-[ACCOUNT-ID] --force

# Deactivate virtual environment
deactivate
```

## 🎯 Success Criteria

Your deployment is successful when:

✅ **Infrastructure**: All AWS resources created without errors  
✅ **Lambda Functions**: All 5 functions deployed and testable  
✅ **Demo Script**: Runs without errors and shows realistic output  
✅ **Monitoring**: CloudWatch dashboards accessible  
✅ **Tests**: All unit tests pass  

## 🚀 Next Steps

After successful deployment:

1. **Customize**: Modify threat detection rules for your environment
2. **Integrate**: Connect with your existing security tools
3. **Scale**: Deploy to multiple AWS accounts/regions
4. **Enhance**: Add custom honeypot types
5. **Monitor**: Set up alerts for system health

---

**🎉 Congratulations!** You've successfully deployed SecureShield AI and are ready to demonstrate its capabilities at your hackathon! 