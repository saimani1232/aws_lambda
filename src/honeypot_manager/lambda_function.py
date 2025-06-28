"""
SecureShield AI - Honeypot Manager
Dynamically creates and manages decoy resources based on attack patterns.
"""

import json
import logging
import os
import random
import string
from datetime import datetime, timezone
from typing import Dict, Any, List

import boto3
import structlog

logger = structlog.get_logger()

# Initialize AWS clients
ec2 = boto3.resource('ec2')
s3 = boto3.client('s3')
rds = boto3.client('rds')
iam = boto3.client('iam')

# Configuration
HONEYPOT_VPC_ID = os.getenv('HONEYPOT_VPC_ID')
HONEYPOT_SUBNET_IDS = os.getenv('HONEYPOT_SUBNET_IDS', '').split(',')
HONEYPOT_SECURITY_GROUP_ID = os.getenv('HONEYPOT_SECURITY_GROUP_ID')

class HoneypotManager:
    """Manages dynamic honeypot creation and lifecycle."""
    
    def __init__(self):
        self.honeypot_configs = {
            'web_server': self._create_web_server_honeypot,
            'database': self._create_database_honeypot,
            'file_server': self._create_file_server_honeypot,
            'api_endpoint': self._create_api_honeypot
        }
    
    def adapt_honeypots(self, attack_patterns: Dict[str, Any], threat_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt honeypots based on attack patterns."""
        try:
            logger.info("adapting_honeypots", threat_level=threat_assessment.get('threat_level'))
            
            # Determine which honeypots to create based on attack patterns
            honeypots_to_create = self._determine_honeypot_types(attack_patterns)
            
            # Create honeypots
            created_honeypots = []
            for honeypot_type in honeypots_to_create:
                try:
                    honeypot = self.honeypot_configs[honeypot_type](attack_patterns)
                    created_honeypots.append(honeypot)
                except Exception as e:
                    logger.error(f"failed_to_create_{honeypot_type}_honeypot", error=str(e))
            
            # Update existing honeypots
            updated_honeypots = self._update_existing_honeypots(attack_patterns)
            
            return {
                'created_honeypots': created_honeypots,
                'updated_honeypots': updated_honeypots,
                'adaptation_reason': self._get_adaptation_reason(attack_patterns),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error("honeypot_adaptation_failed", error=str(e))
            raise
    
    def _determine_honeypot_types(self, attack_patterns: Dict[str, Any]) -> List[str]:
        """Determine which types of honeypots to create based on attack patterns."""
        honeypot_types = []
        
        attack_vectors = attack_patterns.get('attack_vectors', [])
        tools_used = attack_patterns.get('tools_used', [])
        
        # Web server honeypot for web-based attacks
        if any(tool in tools_used for tool in ['sqlmap', 'nikto', 'dirb']):
            honeypot_types.append('web_server')
        
        # Database honeypot for database attacks
        if 'sqlmap' in tools_used or 'database' in attack_vectors:
            honeypot_types.append('database')
        
        # File server honeypot for file access attempts
        if 'data_access' in attack_vectors:
            honeypot_types.append('file_server')
        
        # API honeypot for API-based attacks
        if 'api' in attack_vectors or any(tool in tools_used for tool in ['burp', 'zap']):
            honeypot_types.append('api_endpoint')
        
        return honeypot_types
    
    def _create_web_server_honeypot(self, attack_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Create a web server honeypot."""
        try:
            honeypot_id = f"web-honeypot-{self._generate_id()}"
            
            # Create EC2 instance for web server
            instance = ec2.create_instances(
                ImageId='ami-0c02fb55956c7d316',  # Amazon Linux 2
                MinCount=1,
                MaxCount=1,
                InstanceType='t3.micro',
                SubnetId=random.choice(HONEYPOT_SUBNET_IDS) if HONEYPOT_SUBNET_IDS else None,
                SecurityGroupIds=[HONEYPOT_SECURITY_GROUP_ID] if HONEYPOT_SECURITY_GROUP_ID else [],
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': honeypot_id},
                            {'Key': 'Purpose', 'Value': 'Honeypot'},
                            {'Key': 'Type', 'Value': 'WebServer'},
                            {'Key': 'CreatedBy', 'Value': 'SecureShieldAI'}
                        ]
                    }
                ],
                UserData=self._get_web_server_user_data()
            )[0]
            
            logger.info("web_server_honeypot_created", instance_id=instance.id, honeypot_id=honeypot_id)
            
            return {
                'honeypot_id': honeypot_id,
                'type': 'web_server',
                'instance_id': instance.id,
                'public_ip': instance.public_ip_address,
                'creation_time': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error("web_server_honeypot_creation_failed", error=str(e))
            raise
    
    def _create_database_honeypot(self, attack_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Create a database honeypot."""
        try:
            honeypot_id = f"db-honeypot-{self._generate_id()}"
            
            # Create RDS instance
            db_instance = rds.create_db_instance(
                DBInstanceIdentifier=honeypot_id,
                DBInstanceClass='db.t3.micro',
                Engine='mysql',
                MasterUsername='admin',
                MasterUserPassword=self._generate_password(),
                AllocatedStorage=20,
                VpcSecurityGroupIds=[HONEYPOT_SECURITY_GROUP_ID] if HONEYPOT_SECURITY_GROUP_ID else [],
                DBSubnetGroupName='default',
                PubliclyAccessible=True,
                Tags=[
                    {'Key': 'Purpose', 'Value': 'Honeypot'},
                    {'Key': 'Type', 'Value': 'Database'},
                    {'Key': 'CreatedBy', 'Value': 'SecureShieldAI'}
                ]
            )
            
            logger.info("database_honeypot_created", db_instance_id=db_instance['DBInstance']['DBInstanceIdentifier'])
            
            return {
                'honeypot_id': honeypot_id,
                'type': 'database',
                'db_instance_id': db_instance['DBInstance']['DBInstanceIdentifier'],
                'endpoint': db_instance['DBInstance'].get('Endpoint', {}).get('Address'),
                'creation_time': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error("database_honeypot_creation_failed", error=str(e))
            raise
    
    def _create_file_server_honeypot(self, attack_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Create a file server honeypot."""
        try:
            honeypot_id = f"file-honeypot-{self._generate_id()}"
            
            # Create S3 bucket with fake sensitive data
            bucket_name = f"honeypot-files-{self._generate_id()}"
            
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': 'us-east-1'}
            )
            
            # Upload fake sensitive files
            self._upload_fake_files(bucket_name)
            
            # Make bucket publicly readable (honeypot lure)
            s3.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "PublicReadGetObject",
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "s3:GetObject",
                            "Resource": f"arn:aws:s3:::{bucket_name}/*"
                        }
                    ]
                })
            )
            
            logger.info("file_server_honeypot_created", bucket_name=bucket_name, honeypot_id=honeypot_id)
            
            return {
                'honeypot_id': honeypot_id,
                'type': 'file_server',
                'bucket_name': bucket_name,
                'url': f"https://{bucket_name}.s3.amazonaws.com/",
                'creation_time': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error("file_server_honeypot_creation_failed", error=str(e))
            raise
    
    def _create_api_honeypot(self, attack_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Create an API endpoint honeypot."""
        try:
            honeypot_id = f"api-honeypot-{self._generate_id()}"
            
            # Create API Gateway (simplified - in practice would use API Gateway)
            # For demo purposes, we'll create an EC2 instance with a simple API
            instance = ec2.create_instances(
                ImageId='ami-0c02fb55956c7d316',
                MinCount=1,
                MaxCount=1,
                InstanceType='t3.micro',
                SubnetId=random.choice(HONEYPOT_SUBNET_IDS) if HONEYPOT_SUBNET_IDS else None,
                SecurityGroupIds=[HONEYPOT_SECURITY_GROUP_ID] if HONEYPOT_SECURITY_GROUP_ID else [],
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': honeypot_id},
                            {'Key': 'Purpose', 'Value': 'Honeypot'},
                            {'Key': 'Type', 'Value': 'API'},
                            {'Key': 'CreatedBy', 'Value': 'SecureShieldAI'}
                        ]
                    }
                ],
                UserData=self._get_api_server_user_data()
            )[0]
            
            logger.info("api_honeypot_created", instance_id=instance.id, honeypot_id=honeypot_id)
            
            return {
                'honeypot_id': honeypot_id,
                'type': 'api_endpoint',
                'instance_id': instance.id,
                'public_ip': instance.public_ip_address,
                'api_endpoint': f"http://{instance.public_ip_address}/api/v1/",
                'creation_time': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error("api_honeypot_creation_failed", error=str(e))
            raise
    
    def _update_existing_honeypots(self, attack_patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Update existing honeypots based on attack patterns."""
        updated_honeypots = []
        
        try:
            # Find existing honeypots
            instances = ec2.instances.filter(
                Filters=[
                    {'Name': 'tag:Purpose', 'Values': ['Honeypot']},
                    {'Name': 'instance-state-name', 'Values': ['running']}
                ]
            )
            
            for instance in instances:
                # Update honeypot configuration based on attack patterns
                updated_config = self._adapt_honeypot_config(instance, attack_patterns)
                updated_honeypots.append(updated_config)
            
            logger.info("existing_honeypots_updated", count=len(updated_honeypots))
            
        except Exception as e:
            logger.error("failed_to_update_existing_honeypots", error=str(e))
        
        return updated_honeypots
    
    def _adapt_honeypot_config(self, instance, attack_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt honeypot configuration based on attack patterns."""
        # This would involve updating the honeypot's configuration
        # For now, we'll just return basic info
        return {
            'instance_id': instance.id,
            'adaptation_type': 'configuration_update',
            'adaptation_time': datetime.now(timezone.utc).isoformat()
        }
    
    def _get_adaptation_reason(self, attack_patterns: Dict[str, Any]) -> str:
        """Get the reason for honeypot adaptation."""
        reasons = []
        
        if attack_patterns.get('attack_vectors'):
            reasons.append(f"Attack vectors: {', '.join(attack_patterns['attack_vectors'])}")
        
        if attack_patterns.get('tools_used'):
            reasons.append(f"Tools detected: {', '.join(attack_patterns['tools_used'])}")
        
        return "; ".join(reasons) if reasons else "General threat pattern detected"
    
    def _generate_id(self) -> str:
        """Generate a unique ID for honeypots."""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    def _generate_password(self) -> str:
        """Generate a random password."""
        return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=16))
    
    def _get_web_server_user_data(self) -> str:
        """Get user data script for web server honeypot."""
        return """#!/bin/bash
yum update -y
yum install -y httpd php
systemctl start httpd
systemctl enable httpd

# Create fake sensitive files
echo "Fake employee data" > /var/www/html/employees.csv
echo "Fake financial data" > /var/www/html/financial.xlsx
echo "Fake customer data" > /var/www/html/customers.json

# Create vulnerable PHP page
cat > /var/www/html/admin.php << 'EOF'
<?php
if(isset($_POST['username']) && isset($_POST['password'])) {
    $username = $_POST['username'];
    $password = $_POST['password'];
    
    // Log login attempts
    file_put_contents('/var/log/honeypot.log', date('Y-m-d H:i:s') . " Login attempt: $username from " . $_SERVER['REMOTE_ADDR'] . "\n", FILE_APPEND);
    
    // Always show "incorrect" but make it look real
    echo "Invalid username or password";
}
?>
<form method="post">
Username: <input type="text" name="username"><br>
Password: <input type="password" name="password"><br>
<input type="submit" value="Login">
</form>
EOF

# Set permissions
chown -R apache:apache /var/www/html
chmod -R 755 /var/www/html
"""
    
    def _get_api_server_user_data(self) -> str:
        """Get user data script for API server honeypot."""
        return """#!/bin/bash
yum update -y
yum install -y python3 pip

# Create simple API server
cat > /home/ec2-user/api_server.py << 'EOF'
from flask import Flask, request, jsonify
import json
import datetime

app = Flask(__name__)

@app.route('/api/v1/users', methods=['GET'])
def get_users():
    # Log API access
    with open('/var/log/honeypot_api.log', 'a') as f:
        f.write(f"{datetime.datetime.now()} - API access from {request.remote_addr}\n")
    
    return jsonify({
        "users": [
            {"id": 1, "name": "John Doe", "email": "john@company.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@company.com"}
        ]
    })

@app.route('/api/v1/admin', methods=['POST'])
def admin_endpoint():
    # Log admin access attempts
    with open('/var/log/honeypot_api.log', 'a') as f:
        f.write(f"{datetime.datetime.now()} - Admin access attempt from {request.remote_addr}\n")
    
    return jsonify({"error": "Unauthorized"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
EOF

# Install Flask
pip3 install flask

# Start API server
nohup python3 /home/ec2-user/api_server.py > /var/log/api_server.log 2>&1 &
"""

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler for honeypot management."""
    try:
        logger.info("honeypot_management_started")
        
        detail = event.get('detail', {})
        attack_patterns = detail.get('attack_patterns', {})
        threat_assessment = detail.get('threat_assessment', {})
        
        manager = HoneypotManager()
        result = manager.adapt_honeypots(attack_patterns, threat_assessment)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Honeypot adaptation completed',
                'result': result
            })
        }
        
    except Exception as e:
        logger.error("honeypot_management_failed", error=str(e))
        raise 