#!/usr/bin/env python3
"""Test script to verify AI models work correctly"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_openrouter():
    """Test OpenRouter API"""
    print("Testing OpenRouter API...")
    from ai.openrouter import call_openrouter
    
    # Get API key from environment or input
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        api_key = input("Enter your OpenRouter API key: ")
    
    try:
        response = call_openrouter(
            prompt="Hello, who are you?",
            model="mistralai/mistral-7b-instruct:free",
            api_key=api_key
        )
        print(f"✅ OpenRouter test successful!")
        print(f"Response: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ OpenRouter test failed: {e}")
        return False

def test_auto_rotate():
    """Test Auto Rotate mode"""
    print("\nTesting Auto Rotate mode...")
    from ai.auto_rotate import run_auto_rotate
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        api_key = input("Enter your OpenRouter API key: ")
    
    try:
        response = run_auto_rotate(
            prompt="Hello, who are you?",
            openrouter_key=api_key
        )
        print(f"✅ Auto Rotate test successful!")
        print(f"Response: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Auto Rotate test failed: {e}")
        return False

def test_model_router():
    """Test Model Router"""
    print("\nTesting Model Router...")
    from ai.model_router import route_request
    from bot.user_state import set_user_model
    
    # Test with OpenRouter mode
    user_id = 12345
    set_user_model(user_id, "openrouter_mistral")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        api_key = input("Enter your OpenRouter API key: ")
    
    try:
        response = route_request(
            user_id=user_id,
            prompt="Hello, who are you?",
            openrouter_key=api_key
        )
        print(f"✅ Model Router test successful!")
        print(f"Response: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Model Router test failed: {e}")
        return False

def test_master_prompt():
    """Test Master Prompt integration"""
    print("\nTesting Master Prompt...")
    try:
        with open("MASTER_PROMPT.txt", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "{USER_INPUT_HERE}" in content:
            print("✅ Master Prompt loaded successfully")
            print(f"Length: {len(content)} characters")
            
            # Test replacement
            test_input = "make a todo app"
            replaced = content.replace("{USER_INPUT_HERE}", test_input)
            print(f"✅ Prompt replacement works")
            return True
        else:
            print("❌ Master Prompt missing placeholder")
            return False
    except Exception as e:
        print(f"❌ Master Prompt test failed: {e}")
        return False

def main():
    print("🧪 Testing Telegram AI Project Builder Bot Components")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Master Prompt
    if test_master_prompt():
        tests_passed += 1
    
    # Test 2: OpenRouter
    if test_openrouter():
        tests_passed += 1
    
    # Test 3: Auto Rotate
    if test_auto_rotate():
        tests_passed += 1
    
    # Test 4: Model Router
    if test_model_router():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! Your bot should work correctly.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)