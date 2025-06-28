#!/usr/bin/env python3
"""
SecureShield AI - Demo Script
Simulates attacks and demonstrates the honeypot system in action.
Perfect for hackathon presentations and demonstrations.
"""

import json
import time
import random
import argparse
import requests
import boto3
from datetime import datetime, timezone
from typing import Dict, Any, List
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

class SecureShieldDemo:
    """Demo class for SecureShield AI presentation."""
    
    def __init__(self, environment: str = "dev"):
        self.environment = environment
        self.session = boto3.Session()
        self.cloudwatch = self.session.client('cloudwatch')
        self.eventbridge = self.session.client('events')
        self.dynamodb = self.session.resource('dynamodb')
        
        # Load configuration
        self.load_config()
        
    def load_config(self):
        """Load demo configuration."""
        try:
            with open('outputs/terraform_outputs.json', 'r') as f:
                outputs = json.load(f)
                self.threat_intel_table = outputs.get('threat_intel_table_name', {}).get('value')
                self.waf_web_acl_arn = outputs.get('waf_web_acl_arn', {}).get('value')
        except FileNotFoundError:
            logger.warning("Terraform outputs not found, using default values")
            self.threat_intel_table = "secure-shield-threat-intel"
            self.waf_web_acl_arn = "arn:aws:wafv2:us-east-1:123456789012:regional/webacl/secure-shield-waf"
    
    def run_demo(self):
        """Run the complete demo sequence."""
        print("🚀 SecureShield AI - Live Demo")
        print("=" * 50)
        
        # Step 1: Show normal operations
        self.demo_step_1_normal_operations()
        
        # Step 2: Simulate reconnaissance attack
        self.demo_step_2_reconnaissance_attack()
        
        # Step 3: Simulate brute force attack
        self.demo_step_3_brute_force_attack()
        
        # Step 4: Show automated response
        self.demo_step_4_automated_response()
        
        # Step 5: Show intelligence gathering
        self.demo_step_5_intelligence_gathering()
        
        # Step 6: Show adaptive honeypots
        self.demo_step_6_adaptive_honeypots()
        
        print("\n✅ Demo completed successfully!")
        print("🎯 SecureShield AI is protecting your infrastructure!")
    
    def demo_step_1_normal_operations(self):
        """Step 1: Show normal operations dashboard."""
        print("\n📊 Step 1: Normal Operations Dashboard")
        print("-" * 40)
        
        # Simulate normal traffic
        normal_events = [
            {"event": "DescribeInstances", "source_ip": "10.0.1.100", "user": "admin"},
            {"event": "ListBuckets", "source_ip": "10.0.1.101", "user": "developer"},
            {"event": "GetObject", "source_ip": "10.0.1.102", "user": "analyst"}
        ]
        
        for event in normal_events:
            print(f"✅ Normal activity: {event['user']} from {event['source_ip']} - {event['event']}")
            time.sleep(0.5)
        
        print("📈 All systems operational - No threats detected")
        time.sleep(2)
    
    def demo_step_2_reconnaissance_attack(self):
        """Step 2: Simulate reconnaissance attack."""
        print("\n🔍 Step 2: Reconnaissance Attack Detection")
        print("-" * 40)
        
        # Simulate suspicious reconnaissance activity
        recon_events = [
            {"event": "DescribeInstances", "source_ip": "192.168.1.50", "user_agent": "nmap/7.80"},
            {"event": "DescribeSecurityGroups", "source_ip": "192.168.1.50", "user_agent": "nmap/7.80"},
            {"event": "DescribeVpcs", "source_ip": "192.168.1.50", "user_agent": "nmap/7.80"},
            {"event": "ListBuckets", "source_ip": "192.168.1.50", "user_agent": "nmap/7.80"},
            {"event": "GetBucketPolicy", "source_ip": "192.168.1.50", "user_agent": "nmap/7.80"}
        ]
        
        print("🚨 Suspicious activity detected!")
        for i, event in enumerate(recon_events, 1):
            print(f"⚠️  Reconnaissance attempt {i}: {event['event']} from {event['source_ip']}")
            print(f"   Tool detected: {event['user_agent']}")
            time.sleep(0.8)
        
        print("🤖 AI Analysis: Reconnaissance pattern detected")
        print("📊 Threat Level: MEDIUM")
        print("🎯 Category: Reconnaissance")
        time.sleep(2)
    
    def demo_step_3_brute_force_attack(self):
        """Step 3: Simulate brute force attack."""
        print("\n💥 Step 3: Brute Force Attack Detection")
        print("-" * 40)
        
        # Simulate brute force attempts
        brute_force_events = []
        for i in range(10):
            event = {
                "event": "GetUser",
                "source_ip": "203.0.113.25",
                "user_agent": "sqlmap/1.6.12",
                "error": "AccessDenied"
            }
            brute_force_events.append(event)
        
        print("🚨 BRUTE FORCE ATTACK DETECTED!")
        print(f"🔥 {len(brute_force_events)} failed attempts from 203.0.113.25")
        print("🔧 Tool: sqlmap detected")
        print("⏰ Time pattern: Rapid successive attempts")
        
        for i in range(5):  # Show first 5 attempts
            print(f"   ❌ Attempt {i+1}: Access denied")
            time.sleep(0.3)
        
        print("🤖 AI Analysis: Brute force attack pattern confirmed")
        print("📊 Threat Level: HIGH")
        print("🎯 Category: Brute Force, Data Exfiltration")
        time.sleep(2)
    
    def demo_step_4_automated_response(self):
        """Step 4: Show automated response actions."""
        print("\n⚡ Step 4: Automated Response Execution")
        print("-" * 40)
        
        response_actions = [
            "🔒 Blocking IP 203.0.113.25 in WAF",
            "🛡️  Updating Security Groups",
            "📧 Sending HIGH priority alert to Slack",
            "🎫 Creating JIRA incident ticket",
            "📊 Updating threat intelligence database"
        ]
        
        for action in response_actions:
            print(f"⚡ {action}")
            time.sleep(0.8)
        
        print("✅ Automated response completed in < 30 seconds")
        print("🛡️  Threat contained and isolated")
        time.sleep(2)
    
    def demo_step_5_intelligence_gathering(self):
        """Step 5: Show intelligence gathering and analysis."""
        print("\n🧠 Step 5: Intelligence Gathering & Analysis")
        print("-" * 40)
        
        # Simulate threat intelligence data
        threat_intel = {
            "attacker_ip": "203.0.113.25",
            "attack_patterns": ["brute_force", "sql_injection", "reconnaissance"],
            "tools_used": ["sqlmap", "nmap", "dirb"],
            "geographic_location": "Unknown",
            "threat_actor_profile": "Automated scanning bot",
            "first_seen": "2024-01-15T10:30:00Z",
            "attack_count": 47,
            "targeted_resources": ["S3 buckets", "EC2 instances", "RDS databases"]
        }
        
        print("📊 Threat Intelligence Analysis:")
        print(f"   🎯 Attacker IP: {threat_intel['attacker_ip']}")
        print(f"   🔧 Tools Used: {', '.join(threat_intel['tools_used'])}")
        print(f"   📈 Attack Count: {threat_intel['attack_count']} attempts")
        print(f"   🎭 Threat Actor: {threat_intel['threat_actor_profile']}")
        print(f"   🎯 Targets: {', '.join(threat_intel['targeted_resources'])}")
        
        print("\n🤖 AI Behavioral Analysis:")
        print("   📊 Confidence: 94%")
        print("   🎯 Prediction: Likely to attempt data exfiltration")
        print("   ⚠️  Recommendation: Deploy additional honeypots")
        time.sleep(2)
    
    def demo_step_6_adaptive_honeypots(self):
        """Step 6: Show adaptive honeypot creation."""
        print("\n🎣 Step 6: Adaptive Honeypot Deployment")
        print("-" * 40)
        
        # Simulate honeypot creation
        honeypots = [
            {
                "type": "Database Honeypot",
                "purpose": "Attract SQL injection attempts",
                "endpoint": "honeypot-db-123.region.amazonaws.com",
                "fake_data": "Employee records, Financial data"
            },
            {
                "type": "Web Server Honeypot",
                "purpose": "Attract web-based attacks",
                "endpoint": "honeypot-web-456.region.amazonaws.com",
                "fake_data": "Admin panel, User credentials"
            },
            {
                "type": "API Honeypot",
                "purpose": "Attract API-based attacks",
                "endpoint": "honeypot-api-789.region.amazonaws.com",
                "fake_data": "User API keys, Internal endpoints"
            }
        ]
        
        print("🎣 Deploying Adaptive Honeypots:")
        for honeypot in honeypots:
            print(f"   🚀 Creating {honeypot['type']}")
            print(f"      Purpose: {honeypot['purpose']}")
            print(f"      Endpoint: {honeypot['endpoint']}")
            print(f"      Bait: {honeypot['fake_data']}")
            time.sleep(0.8)
        
        print("\n🎯 Honeypot Strategy:")
        print("   📊 Monitoring attacker behavior")
        print("   🎣 Feeding false information")
        print("   📈 Gathering intelligence")
        print("   🛡️  Protecting real resources")
        time.sleep(2)
    
    def show_dashboard_metrics(self):
        """Show real-time dashboard metrics."""
        print("\n📊 Real-Time Security Dashboard")
        print("=" * 50)
        
        metrics = {
            "threats_detected_today": 12,
            "automated_responses": 8,
            "honeypots_active": 5,
            "ips_blocked": 3,
            "false_positives": 1,
            "response_time_avg": "2.3 seconds",
            "threat_intelligence_entries": 47,
            "system_uptime": "99.9%"
        }
        
        for metric, value in metrics.items():
            print(f"📈 {metric.replace('_', ' ').title()}: {value}")
            time.sleep(0.3)
    
    def simulate_live_attack(self):
        """Simulate a live attack for real-time demonstration."""
        print("\n🔥 LIVE ATTACK SIMULATION")
        print("=" * 50)
        
        attack_steps = [
            "🚨 New attack detected from 198.51.100.75",
            "🔍 Analyzing attack pattern...",
            "🤖 AI Classification: Data Exfiltration Attempt",
            "📊 Threat Level: CRITICAL",
            "⚡ Executing automated response...",
            "🔒 Blocking IP in WAF...",
            "🛡️  Isolating affected resources...",
            "📧 Sending emergency alert...",
            "🎫 Creating critical incident ticket...",
            "✅ Threat contained in 15 seconds!"
        ]
        
        for step in attack_steps:
            print(step)
            time.sleep(1)
    
    def show_business_value(self):
        """Show business value and ROI."""
        print("\n💰 Business Value & ROI")
        print("=" * 50)
        
        value_metrics = {
            "Security Incidents Prevented": "47 this month",
            "Response Time Reduction": "From 4 hours to 30 seconds",
            "Security Team Efficiency": "85% improvement",
            "False Positive Reduction": "92% reduction",
            "Compliance Coverage": "SOC 2, GDPR, HIPAA ready",
            "Cost Savings": "$150K annually",
            "Threat Intelligence Value": "Real-time insights",
            "Scalability": "Multi-account, multi-region"
        }
        
        for metric, value in value_metrics.items():
            print(f"💎 {metric}: {value}")
            time.sleep(0.5)

def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="SecureShield AI Demo")
    parser.add_argument("--environment", default="dev", help="Environment (dev/staging/prod)")
    parser.add_argument("--demo-type", choices=["full", "quick", "live"], default="full", 
                       help="Demo type: full, quick, or live attack simulation")
    
    args = parser.parse_args()
    
    demo = SecureShieldDemo(args.environment)
    
    if args.demo_type == "full":
        demo.run_demo()
        demo.show_dashboard_metrics()
        demo.show_business_value()
    elif args.demo_type == "quick":
        demo.demo_step_2_reconnaissance_attack()
        demo.demo_step_4_automated_response()
        demo.show_dashboard_metrics()
    elif args.demo_type == "live":
        demo.simulate_live_attack()
        demo.show_dashboard_metrics()

if __name__ == "__main__":
    main() 