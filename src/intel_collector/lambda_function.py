"""
SecureShield AI - Intelligence Collector
Analyzes attacker behavior patterns and stores threat intelligence in DynamoDB.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, List

import boto3
import structlog

logger = structlog.get_logger()

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime')

# Configuration
THREAT_INTEL_TABLE = os.getenv('THREAT_INTEL_TABLE', 'secure-shield-threat-intel')
ATTACKER_PROFILES_TABLE = os.getenv('ATTACKER_PROFILES_TABLE', 'secure-shield-attacker-profiles')

class IntelligenceCollector:
    """Collects and analyzes threat intelligence from security events."""
    
    def __init__(self):
        self.threat_intel_table = dynamodb.Table(THREAT_INTEL_TABLE)
        self.attacker_profiles_table = dynamodb.Table(ATTACKER_PROFILES_TABLE)
    
    def collect_intelligence(self, threat_assessment: Dict[str, Any], original_event: Dict[str, Any]) -> Dict[str, Any]:
        """Collect intelligence from security event."""
        try:
            # Extract event details
            event_details = self._extract_event_details(original_event)
            
            # Analyze attack patterns
            attack_patterns = self._analyze_attack_patterns(event_details, threat_assessment)
            
            # Update attacker profile
            attacker_profile = self._update_attacker_profile(event_details, attack_patterns)
            
            # Store intelligence
            intelligence_id = self._store_intelligence(event_details, threat_assessment, attack_patterns)
            
            # Trigger additional analysis if needed
            if threat_assessment.get('threat_level') in ['HIGH', 'CRITICAL']:
                self._trigger_deep_analysis(event_details, threat_assessment)
            
            logger.info(
                "intelligence_collected",
                intelligence_id=intelligence_id,
                attacker_ip=event_details.get('source_ip'),
                threat_level=threat_assessment.get('threat_level')
            )
            
            return {
                'intelligence_id': intelligence_id,
                'attack_patterns': attack_patterns,
                'attacker_profile': attacker_profile,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error("intelligence_collection_failed", error=str(e))
            raise
    
    def _extract_event_details(self, original_event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant details from the original event."""
        detail = original_event.get('detail', {})
        
        return {
            'event_id': detail.get('eventID'),
            'event_name': detail.get('eventName'),
            'event_time': detail.get('eventTime'),
            'source_ip': detail.get('sourceIPAddress'),
            'user_agent': detail.get('userAgent'),
            'user_identity': detail.get('userIdentity', {}),
            'request_parameters': detail.get('requestParameters', {}),
            'response_elements': detail.get('responseElements', {}),
            'error_code': detail.get('errorCode'),
            'error_message': detail.get('errorMessage'),
            'aws_region': detail.get('awsRegion'),
            'event_source': detail.get('eventSource'),
            'event_type': detail.get('eventType'),
            'resources': detail.get('resources', [])
        }
    
    def _analyze_attack_patterns(self, event_details: Dict[str, Any], threat_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze attack patterns from event details."""
        patterns = {
            'attack_vectors': [],
            'tools_used': [],
            'time_patterns': {},
            'geographic_patterns': {},
            'behavioral_patterns': []
        }
        
        # Analyze attack vectors
        event_name = event_details.get('event_name', '')
        if 'Describe' in event_name:
            patterns['attack_vectors'].append('reconnaissance')
        if 'Get' in event_name:
            patterns['attack_vectors'].append('data_access')
        if 'Create' in event_name or 'Put' in event_name:
            patterns['attack_vectors'].append('resource_creation')
        
        # Analyze tools used
        user_agent = event_details.get('user_agent', '').lower()
        if 'nmap' in user_agent:
            patterns['tools_used'].append('nmap')
        if 'sqlmap' in user_agent:
            patterns['tools_used'].append('sqlmap')
        if 'metasploit' in user_agent:
            patterns['tools_used'].append('metasploit')
        
        # Analyze time patterns
        event_time = event_details.get('event_time')
        if event_time:
            dt = datetime.fromisoformat(event_time.replace('Z', '+00:00'))
            patterns['time_patterns'] = {
                'hour': dt.hour,
                'day_of_week': dt.weekday(),
                'is_off_hours': dt.hour < 6 or dt.hour > 22
            }
        
        # Analyze behavioral patterns
        if event_details.get('error_code'):
            patterns['behavioral_patterns'].append('failed_attempts')
        
        if len(event_details.get('resources', [])) > 5:
            patterns['behavioral_patterns'].append('bulk_operations')
        
        return patterns
    
    def _update_attacker_profile(self, event_details: Dict[str, Any], attack_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Update or create attacker profile."""
        source_ip = event_details.get('source_ip')
        if not source_ip:
            return {}
        
        try:
            # Get existing profile
            response = self.attacker_profiles_table.get_item(
                Key={'source_ip': source_ip}
            )
            
            profile = response.get('Item', {
                'source_ip': source_ip,
                'first_seen': event_details.get('event_time'),
                'attack_count': 0,
                'attack_vectors': set(),
                'tools_used': set(),
                'threat_levels': [],
                'last_activity': event_details.get('event_time')
            })
            
            # Update profile
            profile['attack_count'] += 1
            profile['attack_vectors'].update(attack_patterns.get('attack_vectors', []))
            profile['tools_used'].update(attack_patterns.get('tools_used', []))
            profile['last_activity'] = event_details.get('event_time')
            
            # Convert sets to lists for DynamoDB storage
            profile['attack_vectors'] = list(profile['attack_vectors'])
            profile['tools_used'] = list(profile['tools_used'])
            
            # Store updated profile
            self.attacker_profiles_table.put_item(Item=profile)
            
            return profile
            
        except Exception as e:
            logger.error("failed_to_update_attacker_profile", error=str(e))
            return {}
    
    def _store_intelligence(self, event_details: Dict[str, Any], threat_assessment: Dict[str, Any], attack_patterns: Dict[str, Any]) -> str:
        """Store threat intelligence in DynamoDB."""
        try:
            intelligence_id = f"intel_{event_details.get('event_id', 'unknown')}_{int(datetime.now().timestamp())}"
            
            item = {
                'intelligence_id': intelligence_id,
                'event_id': event_details.get('event_id'),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'source_ip': event_details.get('source_ip'),
                'threat_level': threat_assessment.get('threat_level'),
                'risk_score': threat_assessment.get('risk_score'),
                'attack_patterns': attack_patterns,
                'event_details': event_details,
                'threat_categories': threat_assessment.get('categories', []),
                'ttl': int(datetime.now().timestamp()) + (90 * 24 * 60 * 60)  # 90 days TTL
            }
            
            self.threat_intel_table.put_item(Item=item)
            
            return intelligence_id
            
        except Exception as e:
            logger.error("failed_to_store_intelligence", error=str(e))
            raise
    
    def _trigger_deep_analysis(self, event_details: Dict[str, Any], threat_assessment: Dict[str, Any]) -> None:
        """Trigger deep analysis for high/critical threats."""
        try:
            # This would trigger additional analysis Lambda functions
            # For now, we'll log the trigger
            logger.info(
                "deep_analysis_triggered",
                source_ip=event_details.get('source_ip'),
                threat_level=threat_assessment.get('threat_level')
            )
            
        except Exception as e:
            logger.error("failed_to_trigger_deep_analysis", error=str(e))

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler for intelligence collection."""
    try:
        logger.info("intelligence_collection_started")
        
        detail = event.get('detail', {})
        threat_assessment = detail.get('threat_assessment', {})
        original_event = detail.get('original_event', {})
        
        collector = IntelligenceCollector()
        result = collector.collect_intelligence(threat_assessment, original_event)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Intelligence collection completed',
                'result': result
            })
        }
        
    except Exception as e:
        logger.error("intelligence_collection_failed", error=str(e))
        raise 