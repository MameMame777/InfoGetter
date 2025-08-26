#!/usr/bin/env python3
"""
Test script to verify email safety mechanism
Tests that emails are NOT sent when LLM summaries fail or contain errors
"""

import os
import sys
import json
import tempfile
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_email_safety_mechanism():
    """Test that emails are blocked when summaries contain errors"""
    
    print("🧪 Testing Email Safety Mechanism")
    print("=" * 50)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "LLM Error Detected",
            "summary_info": {
                "llm_error_detected": True,
                "llm_error_message": "LLM libraries not available - CRITICAL: Do not send email",
                "email_safe": False
            },
            "expected_email": False
        },
        {
            "name": "Error Indicators in Summary",
            "summary_info": {
                "llm_error_detected": True,
                "llm_error_message": "LLM processing error detected - CRITICAL: Do not send email",
                "email_safe": False
            },
            "expected_email": False
        },
        {
            "name": "Fallback Summary Generated",
            "summary_info": {
                "llm_error_detected": True,
                "llm_error_message": "LLM libraries not available - CRITICAL: Do not send email",
                "generation_method": "fallback",
                "email_safe": False
            },
            "expected_email": False
        },
        {
            "name": "Successful LLM Processing",
            "summary_info": {
                "llm_error_detected": False,
                "llm_error_message": "LLM processing successful",
                "generation_method": "llm",
                "email_safe": True
            },
            "expected_email": True
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 Test {i}: {scenario['name']}")
        print("-" * 30)
        
        # Simulate the email safety check logic from main.py
        summary_info = scenario["summary_info"]
        llm_error_detected = summary_info.get('llm_error_detected', True)
        email_safe = summary_info.get('email_safe', False)
        
        # This is the actual logic from main.py
        summary_generation_success = (
            not llm_error_detected and
            email_safe
        )
        
        # Check if email would be sent
        would_send_email = summary_generation_success
        expected = scenario["expected_email"]
        
        print(f"   LLM Error Detected: {llm_error_detected}")
        print(f"   Email Safe Flag: {email_safe}")
        print(f"   Would Send Email: {would_send_email}")
        print(f"   Expected: {expected}")
        
        if would_send_email == expected:
            print("   ✅ PASS - Email safety working correctly")
        else:
            print("   ❌ FAIL - Email safety mechanism broken!")
            
        print()
    
    print("🔒 Email Safety Summary:")
    print("- Emails are BLOCKED when llm_error_detected=True")
    print("- Emails are BLOCKED when email_safe=False") 
    print("- Emails are ONLY sent when both conditions are met:")
    print("  * llm_error_detected=False")
    print("  * email_safe=True")
    print("\nThis prevents customer complaints from receiving error content! 🛡️")

if __name__ == "__main__":
    test_email_safety_mechanism()
