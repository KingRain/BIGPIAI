#!/usr/bin/env python3
"""
Test script to verify Gemini AI integration
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_gemini_api():
    """Test Gemini API integration"""
    try:
        # Load environment variables
        from app.cv_processor.utils.env_utils import load_env_from_file
        load_env_from_file()
        
        # Test AI client
        from app.cv_processor.utils.ai_client import get_ai_client
        
        print("🔧 Testing Gemini API integration...")
        print(f"GEMINI_API_KEY set: {'✓' if os.getenv('GEMINI_API_KEY') else '✗'}")
        
        client = get_ai_client()
        print("✓ AI client created successfully")
        
        # Simple test prompt
        test_response = client.generate([
            {"role": "user", "content": "Return a simple JSON object with a 'test' key and 'success' value. No other text."}
        ])
        
        print(f"✓ AI response received: {test_response[:100]}...")
        
        result = client.extract_json_from_response(test_response)
        print(f"✓ JSON extracted: {result}")
        
        return True
        
    except Exception as e:
        print(f"✗ AI test failed: {str(e)}")
        return False

def test_cv_processor_imports():
    """Test CV processor module imports"""
    try:
        print("\n🔧 Testing CV processor imports...")
        
        from app.cv_processor.analysis.placeholder_mapper import (
            extract_jinja_placeholders,
            map_jinja_placeholders_to_values
        )
        from app.cv_processor.analysis.cv_parser import extract_raw_cv_text
        from app.cv_processor.analysis.template_analyzer import read_template_full_text
        
        print("✓ All CV processor modules imported successfully")
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {str(e)}")
        return False

def test_placeholder_extraction():
    """Test Jinja placeholder extraction"""
    try:
        print("\n🔧 Testing placeholder extraction...")
        
        from app.cv_processor.analysis.placeholder_mapper import extract_jinja_placeholders
        
        # Test template with Jinja placeholders
        test_template = """
        Name: {{name}}
        Email: {{email}}
        Experience: {{experience}}
        Skills: {{skills}}
        """
        
        placeholders = extract_jinja_placeholders(test_template)
        print(f"✓ Extracted placeholders: {placeholders}")
        
        return len(placeholders) > 0
        
    except Exception as e:
        print(f"✗ Placeholder extraction failed: {str(e)}")
        return False

def test_ai_mapping():
    """Test AI placeholder mapping"""
    try:
        print("\n🔧 Testing AI placeholder mapping...")
        
        from app.cv_processor.analysis.placeholder_mapper import map_jinja_placeholders_to_values
        
        # Test data
        placeholders = ['name', 'email', 'experience']
        resume_text = """
        John Doe
        Software Engineer with 5 years experience
        Email: john.doe@example.com
        Python, JavaScript, React
        """
        template_text = "Name: {{name}}, Email: {{email}}, Experience: {{experience}}"
        
        result = map_jinja_placeholders_to_values(placeholders, resume_text, template_text)
        print(f"✓ AI mapping result: {result}")
        
        return isinstance(result, dict) and len(result) > 0
        
    except Exception as e:
        print(f"✗ AI mapping failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 BIGPIAI CV Processor Test Suite")
    print("=" * 50)
    
    tests = [
        test_cv_processor_imports,
        test_gemini_api,
        test_placeholder_extraction,
        test_ai_mapping
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CV processor is ready.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
