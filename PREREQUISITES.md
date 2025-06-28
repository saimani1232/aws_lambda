# SecureShield AI - Prerequisites Setup Guide

## 🛠️ Required Software

### 1. **AWS CLI** (v2.0+)
```bash
# Windows
# Download from: https://aws.amazon.com/cli/

# macOS
brew install awscli

# Linux (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install awscli

# Verify installation
aws --version
```

### 2. **Terraform** (v1.0+)
```bash
# Windows
# Download from: https://www.terraform.io/downloads.html

# macOS
brew install terraform

# Linux
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs)"
sudo apt-get update && sudo apt-get install terraform

# Verify installation
terraform --version
```

### 3. **Python** (v3.9+)
```bash
# Windows
# Download from: https://www.python.org/downloads/

# macOS
brew install python@3.9

# Linux (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# Verify installation
python3 --version
```

### 4. **Git** (for version control)
```bash
# Windows
# Download from: https://git-scm.com/download/win

# macOS
brew install git

# Linux
sudo apt-get install git

# Verify installation
git --version
```

## 🔐 AWS Account Setup

### 1. **Create AWS Account** (if you don't have one)
- Go to https://aws.amazon.com/
- Click "Create an AWS Account"
- Follow the registration process
- **Note**: You'll need a credit card, but AWS offers free tier

### 2. **Create IAM User** (recommended)
```bash
# Go to AWS Console → IAM → Users → Create User
# Username: secureshield-admin
# Access type: Programmatic access

# Attach policies:
# - AdministratorAccess (for demo purposes)
# - AmazonBedrockFullAccess
# - CloudWatchFullAccess
# - DynamoDBFullAccess
# - EventBridgeFullAccess
# - LambdaFullAccess
# - WAFV2FullAccess
```

### 3. **Configure AWS Credentials**
```bash
aws configure
# AWS Access Key ID: [Your Access Key]
# AWS Secret Access Key: [Your Secret Key]
# Default region name: us-east-1
# Default output format: json

# Verify configuration
aws sts get-caller-identity
```

### 4. **Enable AWS Bedrock**
```bash
# Go to AWS Console → Bedrock
# Click "Get started"
# Request access to:
# - Claude 3 Sonnet
# - Claude 3 Haiku
# - Claude 3 Opus
```

## 🔧 Environment Setup

### 1. **Clone/Setup Project**
```bash
# If you haven't already, navigate to your project
cd /path/to/your/lemi.ai/aws

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

### 2. **Set Environment Variables**
```bash
# Create .env file
cat > .env << EOF
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# External Integrations (Optional for demo)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
JIRA_API_URL=https://your-domain.atlassian.net
JIRA_API_TOKEN=your-jira-api-token
PAGERDUTY_API_KEY=your-pagerduty-api-key
PAGERDUTY_SERVICE_ID=your-service-id

# Threat Intelligence
THREAT_INTEL_API_KEY=your-api-key
EOF

# Load environment variables
# Windows:
set /p < .env
# macOS/Linux:
export $(cat .env | xargs)
```

## 🧪 Test Your Setup

### 1. **Test AWS CLI**
```bash
aws sts get-caller-identity
# Should return your account info
```

### 2. **Test Terraform**
```bash
terraform version
# Should show version 1.0+
```

### 3. **Test Python**
```bash
python3 --version
# Should show Python 3.9+
```

### 4. **Test Dependencies**
```bash
python3 -c "import boto3, structlog, requests; print('All dependencies installed!')"
```

## ⚠️ Important Notes

### **Cost Considerations**
- **Free Tier**: AWS offers 12 months free tier
- **Estimated Costs**: ~$50-100/month for full deployment
- **Demo Mode**: Can run with minimal resources (~$10-20/month)

### **Security Best Practices**
- Use IAM roles with least privilege
- Enable MFA on your AWS account
- Regularly rotate access keys
- Monitor AWS costs

### **Demo Limitations**
- Some features require paid AWS services
- External integrations (Slack, JIRA) are optional
- Can run core functionality without external services

## 🚀 Ready to Deploy?

Once you've completed all prerequisites, you're ready to deploy SecureShield AI!

```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh dev us-east-1
``` 