"""
SecureShield AI - Threat Detection Engine
Analyzes CloudTrail events using AI-powered threat intelligence to detect and categorize security threats.
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

import boto3
from botocore.exceptions import ClientError
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Initialize AWS clients
bedrock = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))
dynamodb = boto3.resource('dynamodb')
eventbridge = boto3.client('events')
cloudwatch = boto3.client('cloudwatch')

# Configuration
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
THREAT_INTEL_TABLE = os.getenv('THREAT_INTEL_TABLE', 'secure-shield-threat-intel')
ALERT_TOPIC_ARN = os.getenv('ALERT_TOPIC_ARN')

# Threat categories and their risk scores
THREAT_CATEGORIES = {
    'reconnaissance': 3,
    'brute_force': 7,
    'data_exfiltration': 9,
    'privilege_escalation': 8,
    'persistence': 6,
    'lateral_movement': 7,
    'command_control': 8,
    'exfiltration': 9,
    'impact': 10
}

class ThreatDetector:
    """AI-powered threat detection engine using AWS Bedrock."""
    
    def __init__(self):
        self.table = dynamodb.Table(THREAT_INTEL_TABLE)
        self.suspicious_patterns = self._load_suspicious_patterns()
    
    def _load_suspicious_patterns(self) -> Dict[str, List[str]]:
        """Load known suspicious patterns for pattern matching."""
        return {
            'api_calls': [
                'DescribeInstances', 'DescribeSecurityGroups', 'DescribeVpcs',
                'ListBuckets', 'GetBucketPolicy', 'DescribeDBInstances',
                'GetUser', 'ListUsers', 'GetRole', 'ListRoles'
            ],
            'ip_patterns': [
                r'^10\.', r'^172\.(1[6-9]|2[0-9]|3[0-1])\.', r'^192\.168\.'
            ],
            'user_agents': [
                'nmap', 'sqlmap', 'nikto', 'dirb', 'gobuster', 'hydra',
                'metasploit', 'burp', 'zap', 'w3af'
            ]
        }
    
    def analyze_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a CloudTrail event for potential threats."""
        try:
            # Extract event details
            event_details = self._extract_event_details(event)
            
            # Perform pattern-based analysis
            pattern_analysis = self._pattern_analysis(event_details)
            
            # Perform AI-powered analysis
            ai_analysis = self._ai_analysis(event_details)
            
            # Combine analyses and determine threat level
            threat_assessment = self._assess_threat_level(pattern_analysis, ai_analysis)
            
            # Log the analysis
            logger.info(
                "threat_analysis_complete",
                event_id=event_details.get('event_id'),
                threat_level=threat_assessment['threat_level'],
                confidence=threat_assessment['confidence'],
                categories=threat_assessment['categories']
            )
            
            return threat_assessment
            
        except Exception as e:
            logger.error("threat_analysis_failed", error=str(e), event=event)
            raise
    
    def _extract_event_details(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant details from CloudTrail event."""
        detail = event.get('detail', {})
        
        return {
            'event_id': detail.get('eventID'),
            'event_name': detail.get('eventName'),
            'event_time': detail.get('eventTime'),
            'user_identity': detail.get('userIdentity', {}),
            'source_ip': detail.get('sourceIPAddress'),
            'user_agent': detail.get('userAgent'),
            'request_parameters': detail.get('requestParameters', {}),
            'response_elements': detail.get('responseElements', {}),
            'error_code': detail.get('errorCode'),
            'error_message': detail.get('errorMessage'),
            'aws_region': detail.get('awsRegion'),
            'event_source': detail.get('eventSource'),
            'event_type': detail.get('eventType')
        }
    
    def _pattern_analysis(self, event_details: Dict[str, Any]) -> Dict[str, Any]:
        """Perform pattern-based threat analysis."""
        patterns_found = []
        risk_score = 0
        
        # Check for suspicious API calls
        event_name = event_details.get('event_name', '')
        if event_name in self.suspicious_patterns['api_calls']:
            patterns_found.append(f'suspicious_api_call:{event_name}')
            risk_score += 2
        
        # Check for suspicious user agents
        user_agent = event_details.get('user_agent', '').lower()
        for suspicious_ua in self.suspicious_patterns['user_agents']:
            if suspicious_ua in user_agent:
                patterns_found.append(f'suspicious_user_agent:{suspicious_ua}')
                risk_score += 5
        
        # Check for error patterns (potential brute force)
        if event_details.get('error_code'):
            patterns_found.append(f'api_error:{event_details["error_code"]}')
            risk_score += 1
        
        # Check for unusual timing patterns
        event_time = event_details.get('event_time')
        if event_time:
            hour = datetime.fromisoformat(event_time.replace('Z', '+00:00')).hour
            if hour < 6 or hour > 22:  # Off-hours activity
                patterns_found.append('off_hours_activity')
                risk_score += 1
        
        return {
            'patterns_found': patterns_found,
            'risk_score': risk_score,
            'confidence': min(risk_score * 10, 100)
        }
    
    def _ai_analysis(self, event_details: Dict[str, Any]) -> Dict[str, Any]:
        """Perform AI-powered threat analysis using AWS Bedrock."""
        try:
            # Prepare prompt for AI analysis
            prompt = self._create_ai_prompt(event_details)
            
            # Call Bedrock
            response = bedrock.invoke_model(
                modelId=BEDROCK_MODEL_ID,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            ai_analysis = json.loads(response_body['content'][0]['text'])
            
            return ai_analysis
            
        except Exception as e:
            logger.error("ai_analysis_failed", error=str(e))
            return {
                'threat_categories': [],
                'confidence': 0,
                'reasoning': f'AI analysis failed: {str(e)}'
            }
    
    def _create_ai_prompt(self, event_details: Dict[str, Any]) -> str:
        """Create a prompt for AI threat analysis."""
        return f"""
You are a cybersecurity threat analyst. Analyze the following AWS CloudTrail event for potential security threats.

Event Details:
- Event Name: {event_details.get('event_name')}
- Source IP: {event_details.get('source_ip')}
- User Agent: {event_details.get('user_agent')}
- Event Time: {event_details.get('event_time')}
- AWS Region: {event_details.get('aws_region')}
- Error Code: {event_details.get('error_code')}
- Error Message: {event_details.get('error_message')}

Analyze this event and respond with a JSON object containing:
1. "threat_categories": List of threat categories this event might belong to (reconnaissance, brute_force, data_exfiltration, privilege_escalation, persistence, lateral_movement, command_control, exfiltration, impact)
2. "confidence": Confidence score (0-100) in your assessment
3. "reasoning": Brief explanation of your analysis
4. "risk_score": Overall risk score (1-10)

Consider:
- Is this normal administrative activity or suspicious?
- Are there indicators of reconnaissance, attack, or data theft?
- Is the timing, source, or pattern unusual?
- Are there any error patterns suggesting failed attacks?

Respond only with valid JSON.
"""
    
    def _assess_threat_level(self, pattern_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Combine pattern and AI analysis to determine overall threat level."""
        # Combine risk scores
        pattern_score = pattern_analysis.get('risk_score', 0)
        ai_score = ai_analysis.get('risk_score', 0)
        combined_score = (pattern_score + ai_score) / 2
        
        # Determine threat level
        if combined_score >= 8:
            threat_level = 'CRITICAL'
        elif combined_score >= 6:
            threat_level = 'HIGH'
        elif combined_score >= 4:
            threat_level = 'MEDIUM'
        elif combined_score >= 2:
            threat_level = 'LOW'
        else:
            threat_level = 'INFO'
        
        # Combine threat categories
        all_categories = set()
        if 'threat_categories' in ai_analysis:
            all_categories.update(ai_analysis['threat_categories'])
        
        # Add categories based on patterns
        patterns = pattern_analysis.get('patterns_found', [])
        for pattern in patterns:
            if 'brute_force' in pattern:
                all_categories.add('brute_force')
            elif 'reconnaissance' in pattern:
                all_categories.add('reconnaissance')
        
        return {
            'threat_level': threat_level,
            'risk_score': combined_score,
            'confidence': max(pattern_analysis.get('confidence', 0), ai_analysis.get('confidence', 0)),
            'categories': list(all_categories),
            'patterns_found': patterns,
            'ai_reasoning': ai_analysis.get('reasoning', ''),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for threat detection.
    
    Args:
        event: EventBridge event containing CloudTrail data
        context: Lambda context
    
    Returns:
        Dict containing threat analysis results
    """
    try:
        logger.info("threat_detection_started", event_id=event.get('id'))
        
        # Initialize threat detector
        detector = ThreatDetector()
        
        # Analyze the event
        threat_assessment = detector.analyze_event(event)
        
        # Store threat intelligence
        if threat_assessment['threat_level'] in ['MEDIUM', 'HIGH', 'CRITICAL']:
            store_threat_intelligence(event, threat_assessment)
        
        # Send to response orchestrator if threat detected
        if threat_assessment['threat_level'] in ['HIGH', 'CRITICAL']:
            trigger_incident_response(event, threat_assessment)
        
        # Send metrics to CloudWatch
        send_metrics(threat_assessment)
        
        logger.info("threat_detection_completed", threat_level=threat_assessment['threat_level'])
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Threat analysis completed',
                'threat_assessment': threat_assessment
            })
        }
        
    except Exception as e:
        logger.error("threat_detection_failed", error=str(e))
        raise

def store_threat_intelligence(event: Dict[str, Any], threat_assessment: Dict[str, Any]) -> None:
    """Store threat intelligence in DynamoDB."""
    try:
        table = dynamodb.Table(THREAT_INTEL_TABLE)
        
        item = {
            'event_id': event.get('id'),
            'timestamp': threat_assessment['timestamp'],
            'threat_level': threat_assessment['threat_level'],
            'risk_score': threat_assessment['risk_score'],
            'categories': threat_assessment['categories'],
            'source_ip': event.get('detail', {}).get('sourceIPAddress'),
            'event_name': event.get('detail', {}).get('eventName'),
            'patterns_found': threat_assessment['patterns_found'],
            'ai_reasoning': threat_assessment['ai_reasoning'],
            'ttl': int(time.time()) + (30 * 24 * 60 * 60)  # 30 days TTL
        }
        
        table.put_item(Item=item)
        logger.info("threat_intelligence_stored", event_id=event.get('id'))
        
    except Exception as e:
        logger.error("failed_to_store_threat_intelligence", error=str(e))

def trigger_incident_response(event: Dict[str, Any], threat_assessment: Dict[str, Any]) -> None:
    """Trigger incident response Lambda for high/critical threats."""
    try:
        response_event = {
            'source': 'secure-shield.threat-detector',
            'detail-type': 'Threat Detected',
            'detail': {
                'original_event': event,
                'threat_assessment': threat_assessment,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        }
        
        eventbridge.put_events(Entries=[response_event])
        logger.info("incident_response_triggered", threat_level=threat_assessment['threat_level'])
        
    except Exception as e:
        logger.error("failed_to_trigger_incident_response", error=str(e))

def send_metrics(threat_assessment: Dict[str, Any]) -> None:
    """Send custom metrics to CloudWatch."""
    try:
        metrics = [
            {
                'MetricName': 'ThreatsDetected',
                'Value': 1,
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'ThreatLevel', 'Value': threat_assessment['threat_level']}
                ]
            },
            {
                'MetricName': 'RiskScore',
                'Value': threat_assessment['risk_score'],
                'Unit': 'None',
                'Dimensions': [
                    {'Name': 'ThreatLevel', 'Value': threat_assessment['threat_level']}
                ]
            }
        ]
        
        cloudwatch.put_metric_data(
            Namespace='SecureShield/ThreatDetection',
            MetricData=metrics
        )
        
    except Exception as e:
        logger.error("failed_to_send_metrics", error=str(e)) 