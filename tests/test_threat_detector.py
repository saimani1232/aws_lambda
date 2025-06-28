"""
Test file for SecureShield AI Threat Detector
"""

import pytest
import json
from unittest.mock import Mock, patch
from src.threat_detector.lambda_function import ThreatDetector, lambda_handler

class TestThreatDetector:
    """Test cases for ThreatDetector class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.detector = ThreatDetector()
        
        # Sample CloudTrail event
        self.sample_event = {
            "version": "0",
            "id": "test-event-id",
            "detail-type": "AWS API Call via CloudTrail",
            "source": "aws.ec2",
            "account": "123456789012",
            "time": "2024-01-15T10:30:00Z",
            "region": "us-east-1",
            "detail": {
                "eventVersion": "1.08",
                "userIdentity": {
                    "type": "IAMUser",
                    "principalId": "AIDACKCEVSQ6C2EXAMPLE",
                    "arn": "arn:aws:iam::123456789012:user/test-user",
                    "accountId": "123456789012",
                    "userName": "test-user"
                },
                "eventTime": "2024-01-15T10:30:00Z",
                "eventSource": "ec2.amazonaws.com",
                "eventName": "DescribeInstances",
                "awsRegion": "us-east-1",
                "sourceIPAddress": "192.168.1.100",
                "userAgent": "aws-cli/2.0.0",
                "requestParameters": {
                    "instancesSet": {
                        "items": []
                    }
                },
                "responseElements": None,
                "requestID": "test-request-id",
                "eventID": "test-event-id"
            }
        }
    
    def test_extract_event_details(self):
        """Test event details extraction."""
        details = self.detector._extract_event_details(self.sample_event)
        
        assert details['event_name'] == "DescribeInstances"
        assert details['source_ip'] == "192.168.1.100"
        assert details['user_agent'] == "aws-cli/2.0.0"
        assert details['aws_region'] == "us-east-1"
    
    def test_pattern_analysis_reconnaissance(self):
        """Test pattern analysis for reconnaissance activity."""
        event_details = {
            'event_name': 'DescribeInstances',
            'source_ip': '192.168.1.50',
            'user_agent': 'nmap/7.80',
            'event_time': '2024-01-15T10:30:00Z'
        }
        
        analysis = self.detector._pattern_analysis(event_details)
        
        assert 'suspicious_api_call:DescribeInstances' in analysis['patterns_found']
        assert 'suspicious_user_agent:nmap' in analysis['patterns_found']
        assert analysis['risk_score'] > 0
    
    def test_pattern_analysis_brute_force(self):
        """Test pattern analysis for brute force activity."""
        event_details = {
            'event_name': 'GetUser',
            'source_ip': '203.0.113.25',
            'user_agent': 'sqlmap/1.6.12',
            'event_time': '2024-01-15T10:30:00Z',
            'error_code': 'AccessDenied'
        }
        
        analysis = self.detector._pattern_analysis(event_details)
        
        assert 'suspicious_user_agent:sqlmap' in analysis['patterns_found']
        assert 'api_error:AccessDenied' in analysis['patterns_found']
        assert analysis['risk_score'] > 5
    
    def test_assess_threat_level_critical(self):
        """Test threat level assessment for critical threats."""
        pattern_analysis = {
            'patterns_found': ['suspicious_user_agent:sqlmap', 'api_error:AccessDenied'],
            'risk_score': 8,
            'confidence': 85
        }
        
        ai_analysis = {
            'threat_categories': ['brute_force', 'data_exfiltration'],
            'confidence': 90,
            'reasoning': 'Multiple failed login attempts detected',
            'risk_score': 9
        }
        
        assessment = self.detector._assess_threat_level(pattern_analysis, ai_analysis)
        
        assert assessment['threat_level'] == 'CRITICAL'
        assert assessment['risk_score'] >= 8
        assert 'brute_force' in assessment['categories']
    
    def test_assess_threat_level_low(self):
        """Test threat level assessment for low threats."""
        pattern_analysis = {
            'patterns_found': [],
            'risk_score': 1,
            'confidence': 20
        }
        
        ai_analysis = {
            'threat_categories': [],
            'confidence': 10,
            'reasoning': 'Normal administrative activity',
            'risk_score': 1
        }
        
        assessment = self.detector._assess_threat_level(pattern_analysis, ai_analysis)
        
        assert assessment['threat_level'] in ['LOW', 'INFO']
        assert assessment['risk_score'] <= 2

class TestLambdaHandler:
    """Test cases for Lambda handler."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.sample_event = {
            "version": "0",
            "id": "test-event-id",
            "detail-type": "AWS API Call via CloudTrail",
            "source": "aws.ec2",
            "account": "123456789012",
            "time": "2024-01-15T10:30:00Z",
            "region": "us-east-1",
            "detail": {
                "eventVersion": "1.08",
                "userIdentity": {
                    "type": "IAMUser",
                    "principalId": "AIDACKCEVSQ6C2EXAMPLE",
                    "arn": "arn:aws:iam::123456789012:user/test-user",
                    "accountId": "123456789012",
                    "userName": "test-user"
                },
                "eventTime": "2024-01-15T10:30:00Z",
                "eventSource": "ec2.amazonaws.com",
                "eventName": "DescribeInstances",
                "awsRegion": "us-east-1",
                "sourceIPAddress": "192.168.1.100",
                "userAgent": "aws-cli/2.0.0",
                "requestParameters": {
                    "instancesSet": {
                        "items": []
                    }
                },
                "responseElements": None,
                "requestID": "test-request-id",
                "eventID": "test-event-id"
            }
        }
    
    @patch('src.threat_detector.lambda_function.store_threat_intelligence')
    @patch('src.threat_detector.lambda_function.trigger_incident_response')
    @patch('src.threat_detector.lambda_function.send_metrics')
    def test_lambda_handler_success(self, mock_send_metrics, mock_trigger_response, mock_store_intel):
        """Test successful Lambda handler execution."""
        context = Mock()
        
        result = lambda_handler(self.sample_event, context)
        
        assert result['statusCode'] == 200
        assert 'threat_assessment' in json.loads(result['body'])
    
    @patch('src.threat_detector.lambda_function.store_threat_intelligence')
    @patch('src.threat_detector.lambda_function.trigger_incident_response')
    @patch('src.threat_detector.lambda_function.send_metrics')
    def test_lambda_handler_high_threat(self, mock_send_metrics, mock_trigger_response, mock_store_intel):
        """Test Lambda handler with high threat event."""
        # Create a high threat event
        high_threat_event = self.sample_event.copy()
        high_threat_event['detail']['eventName'] = 'GetUser'
        high_threat_event['detail']['sourceIPAddress'] = '203.0.113.25'
        high_threat_event['detail']['userAgent'] = 'sqlmap/1.6.12'
        high_threat_event['detail']['errorCode'] = 'AccessDenied'
        
        context = Mock()
        
        result = lambda_handler(high_threat_event, context)
        
        assert result['statusCode'] == 200
        # Verify incident response was triggered
        mock_trigger_response.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__]) 