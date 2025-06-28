#!/bin/bash

# SecureShield AI - Deployment Script
# Deploys the complete serverless security honeypot infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="SecureShield AI"
ENVIRONMENT=${1:-"dev"}
AWS_REGION=${2:-"us-east-1"}

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Install Python dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    cd "$(dirname "$0")/.."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r requirements.txt
    
    log_success "Dependencies installed"
}

# Create S3 bucket for Terraform state
create_terraform_state_bucket() {
    log_info "Creating S3 bucket for Terraform state..."
    
    BUCKET_NAME="secureshield-terraform-state-$(aws sts get-caller-identity --query Account --output text)"
    
    if ! aws s3 ls "s3://$BUCKET_NAME" &> /dev/null; then
        aws s3 mb "s3://$BUCKET_NAME" --region "$AWS_REGION"
        aws s3api put-bucket-versioning \
            --bucket "$BUCKET_NAME" \
            --versioning-configuration Status=Enabled
        aws s3api put-bucket-encryption \
            --bucket "$BUCKET_NAME" \
            --server-side-encryption-configuration '{
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            }'
        log_success "Terraform state bucket created: $BUCKET_NAME"
    else
        log_info "Terraform state bucket already exists: $BUCKET_NAME"
    fi
}

# Deploy infrastructure with Terraform
deploy_infrastructure() {
    log_info "Deploying infrastructure with Terraform..."
    
    cd terraform
    
    # Initialize Terraform
    terraform init
    
    # Plan deployment
    log_info "Planning Terraform deployment..."
    terraform plan \
        -var="environment=$ENVIRONMENT" \
        -var="aws_region=$AWS_REGION" \
        -out=tfplan
    
    # Apply deployment
    log_info "Applying Terraform deployment..."
    terraform apply tfplan
    
    # Get outputs
    log_info "Getting Terraform outputs..."
    terraform output -json > ../outputs/terraform_outputs.json
    
    log_success "Infrastructure deployed successfully"
}

# Deploy Lambda functions
deploy_lambda_functions() {
    log_info "Deploying Lambda functions..."
    
    cd "$(dirname "$0")/.."
    
    # Get outputs from Terraform
    if [ ! -f "outputs/terraform_outputs.json" ]; then
        log_error "Terraform outputs not found. Please run infrastructure deployment first."
        exit 1
    fi
    
    # Deploy each Lambda function
    for function in threat_detector incident_response intel_collector alert_dispatcher honeypot_manager; do
        log_info "Deploying $function Lambda function..."
        ./scripts/deploy_lambda.sh "$function" "$ENVIRONMENT"
    done
    
    log_success "Lambda functions deployed"
}

# Setup monitoring and dashboards
setup_monitoring() {
    log_info "Setting up monitoring and dashboards..."
    
    cd "$(dirname "$0")/.."
    
    # Create CloudWatch dashboards
    python3 scripts/setup_monitoring.py --environment "$ENVIRONMENT"
    
    log_success "Monitoring setup completed"
}

# Setup honeypot infrastructure
setup_honeypots() {
    log_info "Setting up honeypot infrastructure..."
    
    cd "$(dirname "$0")/.."
    
    # Deploy initial honeypots
    python3 scripts/setup_honeypots.py --environment "$ENVIRONMENT"
    
    log_success "Honeypot infrastructure setup completed"
}

# Run tests
run_tests() {
    log_info "Running tests..."
    
    cd "$(dirname "$0")/.."
    
    # Run unit tests
    python3 -m pytest tests/unit/ -v
    
    # Run integration tests
    python3 -m pytest tests/integration/ -v
    
    log_success "Tests completed"
}

# Display deployment summary
display_summary() {
    log_info "Deployment Summary"
    echo "=================="
    echo "Project: $PROJECT_NAME"
    echo "Environment: $ENVIRONMENT"
    echo "Region: $AWS_REGION"
    echo ""
    echo "Deployed Components:"
    echo "- VPC and Networking"
    echo "- Lambda Functions (5 functions)"
    echo "- DynamoDB Tables"
    echo "- EventBridge Rules"
    echo "- WAF Configuration"
    echo "- CloudWatch Dashboards"
    echo "- Honeypot Infrastructure"
    echo ""
    echo "Next Steps:"
    echo "1. Configure external integrations (Slack, JIRA, PagerDuty)"
    echo "2. Test the honeypot deployment"
    echo "3. Monitor the security dashboard"
    echo "4. Review and adjust threat detection rules"
}

# Main deployment function
main() {
    log_info "Starting $PROJECT_NAME deployment..."
    log_info "Environment: $ENVIRONMENT"
    log_info "Region: $AWS_REGION"
    
    # Create outputs directory
    mkdir -p outputs
    
    # Run deployment steps
    check_prerequisites
    install_dependencies
    create_terraform_state_bucket
    deploy_infrastructure
    deploy_lambda_functions
    setup_monitoring
    setup_honeypots
    run_tests
    
    log_success "$PROJECT_NAME deployment completed successfully!"
    display_summary
}

# Handle script arguments
case "${1:-}" in
    "help"|"-h"|"--help")
        echo "Usage: $0 [environment] [region]"
        echo "  environment: dev, staging, prod (default: dev)"
        echo "  region: AWS region (default: us-east-1)"
        echo ""
        echo "Examples:"
        echo "  $0                    # Deploy to dev in us-east-1"
        echo "  $0 prod us-west-2     # Deploy to prod in us-west-2"
        exit 0
        ;;
    *)
        main
        ;;
esac 