@echo off
REM SecureShield AI - Windows Setup Script
REM Automates the complete setup and deployment process on Windows

setlocal enabledelayedexpansion

REM Configuration
set PROJECT_NAME=SecureShield AI
set ENVIRONMENT=%1
if "%ENVIRONMENT%"=="" set ENVIRONMENT=dev
set AWS_REGION=%2
if "%AWS_REGION%"=="" set AWS_REGION=us-east-1

echo 🚀 SecureShield AI - Windows Setup
echo ===================================
echo Environment: %ENVIRONMENT%
echo Region: %AWS_REGION%
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script requires administrator privileges.
    echo Please run as administrator and try again.
    pause
    exit /b 1
)

REM Check prerequisites
echo [INFO] Checking prerequisites...

REM Check Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Check AWS CLI
aws --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] AWS CLI not found!
    echo Please install AWS CLI from https://aws.amazon.com/cli/
    pause
    exit /b 1
)

REM Check Terraform
terraform --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Terraform not found!
    echo Please install Terraform from https://www.terraform.io/downloads.html
    pause
    exit /b 1
)

echo [SUCCESS] Prerequisites check passed

REM Setup Python environment
echo [INFO] Setting up Python environment...

if not exist "venv" (
    python -m venv venv
)

call venv\Scripts\activate.bat

REM Install Python dependencies
pip install -r requirements.txt

if %errorLevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)

echo [SUCCESS] Python environment setup completed

REM Check AWS configuration
echo [INFO] Checking AWS configuration...

aws sts get-caller-identity >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] AWS credentials not configured!
    echo.
    echo Please configure AWS credentials:
    echo 1. Go to AWS Console → IAM → Users → Create User
    echo 2. Attach AdministratorAccess policy
    echo 3. Create access keys
    echo 4. Run: aws configure
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('aws sts get-caller-identity --query Account --output text') do set ACCOUNT_ID=%%i
echo [SUCCESS] AWS configured for account: %ACCOUNT_ID%

REM Create environment file
echo [INFO] Creating environment configuration...

(
echo # AWS Configuration
echo AWS_REGION=%AWS_REGION%
echo AWS_ACCOUNT_ID=%ACCOUNT_ID%
echo.
echo # Bedrock Configuration
echo BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
echo.
echo # External Integrations ^(Optional - leave empty for demo^)
echo SLACK_WEBHOOK_URL=
echo JIRA_API_URL=
echo JIRA_API_TOKEN=
echo PAGERDUTY_API_KEY=
echo PAGERDUTY_SERVICE_ID=
echo.
echo # Threat Intelligence
echo THREAT_INTEL_API_KEY=
) > .env

echo [SUCCESS] Environment file created

REM Check AWS Bedrock access
echo [INFO] Checking AWS Bedrock access...

aws bedrock list-foundation-models --region %AWS_REGION% >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] AWS Bedrock access not enabled!
    echo.
    echo Please enable AWS Bedrock:
    echo 1. Go to AWS Console → Bedrock
    echo 2. Click 'Get started'
    echo 3. Request access to Claude models
    echo 4. Wait for approval ^(usually instant^)
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

echo [SUCCESS] AWS Bedrock access confirmed

REM Create outputs directory
if not exist "outputs" mkdir outputs

REM Deploy infrastructure
echo [INFO] Deploying infrastructure...

if exist "scripts\deploy.sh" (
    REM Convert deploy.sh to Windows format and run
    echo [INFO] Running deployment script...
    
    REM For Windows, we'll run the Python deployment directly
    python scripts\deploy.py %ENVIRONMENT% %AWS_REGION%
) else (
    echo [ERROR] Deployment script not found!
    pause
    exit /b 1
)

if %errorLevel% neq 0 (
    echo [ERROR] Deployment failed!
    pause
    exit /b 1
)

echo [SUCCESS] Infrastructure deployed successfully

REM Test deployment
echo [INFO] Testing deployment...

REM Test Lambda functions
aws lambda list-functions --query "Functions[?contains(FunctionName, 'secure-shield')].FunctionName" --output text | findstr "secure-shield" >nul
if %errorLevel% neq 0 (
    echo [ERROR] Lambda functions not found!
    pause
    exit /b 1
)

echo [SUCCESS] Lambda functions deployed successfully

REM Test DynamoDB tables
aws dynamodb list-tables --query "TableNames[?contains(@, 'secure-shield')]" --output text | findstr "secure-shield" >nul
if %errorLevel% neq 0 (
    echo [ERROR] DynamoDB tables not found!
    pause
    exit /b 1
)

echo [SUCCESS] DynamoDB tables created successfully

REM Run demo
echo [INFO] Running demo...

if exist "scripts\demo.py" (
    python scripts\demo.py --demo-type quick
) else (
    echo [ERROR] Demo script not found!
    pause
    exit /b 1
)

REM Show next steps
echo.
echo [SUCCESS] Setup completed successfully!
echo.
echo 🎉 SecureShield AI is now deployed and ready!
echo.
echo 📊 Available Commands:
echo   python scripts\demo.py --demo-type full    # Full demo
echo   python scripts\demo.py --demo-type quick   # Quick demo
echo   python scripts\demo.py --demo-type live    # Live attack simulation
echo.
echo 🔧 Management Commands:
echo   aws lambda list-functions                   # List Lambda functions
echo   aws dynamodb list-tables                    # List DynamoDB tables
echo   aws cloudwatch list-dashboards              # List CloudWatch dashboards
echo.
echo 📚 Documentation:
echo   README.md                                   # Project overview
echo   PREREQUISITES.md                            # Setup guide
echo   EXECUTION_GUIDE.md                          # Detailed instructions
echo.
echo 🧹 Cleanup ^(when done^):
echo   cd terraform ^&^& terraform destroy           # Remove all resources
echo.
echo 🎯 Ready for your hackathon presentation!
echo.
pause 