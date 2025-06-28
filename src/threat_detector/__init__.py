"""
SecureShield AI - Threat Detection Module
AI-powered threat detection engine for analyzing CloudTrail events.
"""

from .lambda_function import ThreatDetector, lambda_handler

__all__ = ['ThreatDetector', 'lambda_handler']
__version__ = '1.0.0' 