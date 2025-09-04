#!/usr/bin/env python3
"""
Environment Variables Test Script
Test if all required environment variables are properly configured.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

def test_environment_setup():
    """Test environment variable configuration."""
    print("🔧 Testing Environment Configuration")
    print("=" * 50)
    
    # Load environment variables
    env_file = Path('.env')
    if env_file.exists():
        load_dotenv()
        print("✓ .env file found and loaded")
    else:
        print("❌ .env file not found")
        return False
    
    # Test required variables
    required_vars = {
        'SECRET_KEY': 'Flask secret key',
        'JWT_SECRET_KEY': 'JWT secret key'
    }
    
    # Test AI API keys
    ai_vars = {
        'OPENAI_API_KEY': 'OpenAI API key (for Phase 1 & 2)',
        'GEMINI_API_KEY': 'Gemini API key (for Phase 3)'
    }
    
    print("\n📋 Required Variables:")
    all_required_set = True
    for var, description in required_vars.items():
        value = os.getenv(var, '')
        if value and not value.startswith('your-') and not value.startswith('dev-'):
            print(f"✓ {var} - SET")
        else:
            print(f"⚠️  {var} - USING DEFAULT/PLACEHOLDER ({description})")
    
    print("\n🤖 AI API Keys:")
    ai_keys_set = []
    for var, description in ai_vars.items():
        value = os.getenv(var, '')
        if value and not value.startswith('your-') and value != 'placeholder-key':
            print(f"✓ {var} - SET")
            ai_keys_set.append(var)
        else:
            print(f"⚠️  {var} - NOT SET ({description})")
    
    # Test AI client initialization
    print("\n🧪 Testing AI Client Initialization:")
    
    # Test OpenAI client (for Phase 1 & 2)
    if 'OPENAI_API_KEY' in ai_keys_set:
        try:
            from app.routes.modules.phase1.openai_processing import get_openai_client
            client = get_openai_client()
            print("✓ OpenAI client - INITIALIZED")
        except Exception as e:
            print(f"❌ OpenAI client - ERROR: {e}")
    else:
        print("⚠️  OpenAI client - SKIPPED (API key not set)")
    
    # Test Gemini client (for Phase 3)
    if 'GEMINI_API_KEY' in ai_keys_set:
        try:
            from app.cv_processor.utils.ai_client import get_ai_client
            client = get_ai_client()
            print("✓ Gemini client - INITIALIZED")
        except Exception as e:
            print(f"❌ Gemini client - ERROR: {e}")
    else:
        print("⚠️  Gemini client - SKIPPED (API key not set)")
    
    # Summary
    print("\n📊 Summary:")
    if len(ai_keys_set) == 0:
        print("❌ No AI API keys configured - only basic functionality available")
    elif len(ai_keys_set) == 1:
        print(f"⚠️  Partial AI functionality - {ai_keys_set[0]} configured")
    else:
        print("✓ Full AI functionality available - all API keys configured")
    
    print("\n💡 To configure missing API keys:")
    print("   1. Edit the .env file in the project root")
    print("   2. Replace placeholder values with your actual API keys")
    print("   3. Get OpenAI API key from: https://platform.openai.com/api-keys")
    print("   4. Get Gemini API key from: https://makersuite.google.com/app/apikey")
    
    return True

if __name__ == '__main__':
    test_environment_setup()