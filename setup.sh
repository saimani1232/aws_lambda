#!/bin/bash

# SecureShield AI - One-Click Setup Script
# Automates the complete setup and deployment process

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

# Check if running on Windows
is_windows() {
    [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]
}

# Install dependencies based on OS
install_dependencies() {
    log_info "Installing system dependencies..."
    
    if is_windows; then
        log_warning "Windows detected. Please install manually:"
        echo "1. AWS CLI: https://aws.amazon.com/cli/"
        echo "2. Terraform: https://www.terraform.io/downloads.html"
        echo "3. Python: https://www.python.org/downloads/"
        echo ""
        echo "After installation, run this script again."
        exit 1
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if ! command -v brew &> /dev/null; then
            log_info "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        log_info "Installing dependencies via Homebrew..."
        brew install awscli terraform python@3.9 git
    else
        # Linux
        log_info "Installing dependencies via apt..."
        sudo apt-get update
        sudo apt-get install -y awscli python3 python3-pip python3-venv git curl
        
        # Install Terraform
        curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
        sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs)"
        sudo apt-get update && sudo apt-get install -y terraform
    fi
    
    log_success "System dependencies installed"
}

# Setup Python environment
setup_python_env() {
    log_info "Setting up Python environment..."
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    if is_windows; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    # Install Python dependencies
    pip install -r requirements.txt
    
    log_success "Python environment setup completed"
}

# Check AWS configuration
check_aws_config() {
    log_info "Checking AWS configuration..."
    
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured!"
        echo ""
        echo "Please configure AWS credentials:"
        echo "1. Go to AWS Console → IAM → Users → Create User"
        echo "2. Attach AdministratorAccess policy"
        echo "3. Create access keys"
        echo "4. Run: aws configure"
        echo ""
        echo "Then run this script again."
        exit 1
    fi
    
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    log_success "AWS configured for account: $ACCOUNT_ID"
}

# Create environment file
create_env_file() {
    log_info "Creating environment configuration..."
    
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    
    cat > .env << EOF
# AWS Configuration
AWS_REGION=$AWS_REGION
AWS_ACCOUNT_ID=$ACCOUNT_ID

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# External Integrations (Optional - leave empty for demo)
SLACK_WEBHOOK_URL=
JIRA_API_URL=
JIRA_API_TOKEN=
PAGERDUTY_API_KEY=
PAGERDUTY_SERVICE_ID=

# Threat Intelligence
THREAT_INTEL_API_KEY=
EOF
    
    log_success "Environment file created"
}

# Enable AWS Bedrock
enable_bedrock() {
    log_info "Checking AWS Bedrock access..."
    
    if ! aws bedrock list-foundation-models --region $AWS_REGION &> /dev/null; then
        log_warning "AWS Bedrock access not enabled!"
        echo ""
        echo "Please enable AWS Bedrock:"
        echo "1. Go to AWS Console → Bedrock"
        echo "2. Click 'Get started'"
        echo "3. Request access to Claude models"
        echo "4. Wait for approval (usually instant)"
        echo ""
        echo "Then run this script again."
        exit 1
    fi
    
    log_success "AWS Bedrock access confirmed"
}

# Deploy infrastructure
deploy_infrastructure() {
    log_info "Deploying infrastructure..."
    
    # Create outputs directory
    mkdir -p outputs
    
    # Run deployment script
    if [ -f "scripts/deploy.sh" ]; then
        chmod +x scripts/deploy.sh
        ./scripts/deploy.sh $ENVIRONMENT $AWS_REGION
    else
        log_error "Deployment script not found!"
        exit 1
    fi
}

# Test deployment
test_deployment() {
    log_info "Testing deployment..."
    
    # Test Lambda functions
    if aws lambda list-functions --query 'Functions[?contains(FunctionName, `secure-shield`)].FunctionName' --output text | grep -q "secure-shield"; then
        log_success "Lambda functions deployed successfully"
    else
        log_error "Lambda functions not found!"
        exit 1
    fi
    
    # Test DynamoDB tables
    if aws dynamodb list-tables --query 'TableNames[?contains(@, `secure-shield`)]' --output text | grep -q "secure-shield"; then
        log_success "DynamoDB tables created successfully"
    else
        log_error "DynamoDB tables not found!"
        exit 1
    fi
}

# Run demo
run_demo() {
    log_info "Running demo..."
    
    if [ -f "scripts/demo.py" ]; then
        python3 scripts/demo.py --demo-type quick
    else
        log_error "Demo script not found!"
        exit 1
    fi
}

# Show next steps
show_next_steps() {
    log_success "Setup completed successfully!"
    echo ""
    echo "🎉 SecureShield AI is now deployed and ready!"
    echo ""
    echo "📊 Available Commands:"
    echo "  python3 scripts/demo.py --demo-type full    # Full demo"
    echo "  python3 scripts/demo.py --demo-type quick   # Quick demo"
    echo "  python3 scripts/demo.py --demo-type live    # Live attack simulation"
    echo ""
    echo "🔧 Management Commands:"
    echo "  aws lambda list-functions                   # List Lambda functions"
    echo "  aws dynamodb list-tables                    # List DynamoDB tables"
    echo "  aws cloudwatch list-dashboards              # List CloudWatch dashboards"
    echo ""
    echo "📚 Documentation:"
    echo "  README.md                                   # Project overview"
    echo "  PREREQUISITES.md                            # Setup guide"
    echo "  EXECUTION_GUIDE.md                          # Detailed instructions"
    echo ""
    echo "🧹 Cleanup (when done):"
    echo "  cd terraform && terraform destroy           # Remove all resources"
    echo ""
    echo "🎯 Ready for your hackathon presentation!"
}

# Main setup function
main() {
    echo "🚀 SecureShield AI - One-Click Setup"
    echo "====================================="
    echo "Environment: $ENVIRONMENT"
    echo "Region: $AWS_REGION"
    echo ""
    
    # Run setup steps
    install_dependencies
    setup_python_env
    check_aws_config
    create_env_file
    enable_bedrock
    deploy_infrastructure
    test_deployment
    run_demo
    show_next_steps
}

# Handle script arguments
case "${1:-}" in
    "help"|"-h"|"--help")
        echo "Usage: $0 [environment] [region]"
        echo "  environment: dev, staging, prod (default: dev)"
        echo "  region: AWS region (default: us-east-1)"
        echo ""
        echo "Examples:"
        echo "  $0                    # Setup dev in us-east-1"
        echo "  $0 prod us-west-2     # Setup prod in us-west-2"
        exit 0
        ;;
    *)
        main
        ;;
esac 