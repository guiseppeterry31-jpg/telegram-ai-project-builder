#!/usr/bin/env python3
"""Test the API Key Manager functionality"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.api_key_manager import api_key_manager

def test_basic_functionality():
    """Test basic API key manager operations"""
    print("Testing API Key Manager...")
    
    # Test user ID
    test_user_id = 123456789
    
    # Clean up any existing test data
    # Convert to string since APIKeyManager now uses string keys
    user_key = str(test_user_id)
    if user_key in api_key_manager.data:
        del api_key_manager.data[user_key]
        api_key_manager._save_data()
    
    print("1. Testing add_key()...")
    # Add first key
    result = api_key_manager.add_key(test_user_id, "primary", "sk-or-v1-test123", "openrouter")
    assert result == True, "Failed to add first key"
    print("   [OK] Added 'primary' key")
    
    # Try adding duplicate key name
    result = api_key_manager.add_key(test_user_id, "primary", "sk-or-v1-different", "openrouter")
    assert result == False, "Should not allow duplicate key names"
    print("   [OK] Prevented duplicate key name")
    
    # Add second key
    result = api_key_manager.add_key(test_user_id, "backup", "sk-or-v1-backup456", "openrouter")
    assert result == True, "Failed to add second key"
    print("   [OK] Added 'backup' key")
    
    print("\n2. Testing list_keys()...")
    keys = api_key_manager.list_keys(test_user_id)
    assert len(keys) == 2, f"Expected 2 keys, got {len(keys)}"
    print(f"   [OK] Found {len(keys)} keys: {[k['name'] for k in keys]}")
    
    print("\n3. Testing get_selected_key()...")
    selected_key = api_key_manager.get_selected_key(test_user_id)
    assert selected_key == "sk-or-v1-test123", f"First key should be selected, got: {selected_key}"
    print(f"   [OK] Selected key is 'primary': {selected_key[:10]}...")
    
    print("\n4. Testing select_key()...")
    result = api_key_manager.select_key(test_user_id, "backup")
    assert result == True, "Failed to select backup key"
    
    selected_key = api_key_manager.get_selected_key(test_user_id)
    assert selected_key == "sk-or-v1-backup456", f"Backup key should be selected, got: {selected_key}"
    print(f"   [OK] Selected key changed to 'backup': {selected_key[:10]}...")
    
    print("\n5. Testing get_selected_key_info()...")
    key_info = api_key_manager.get_selected_key_info(test_user_id)
    assert key_info["name"] == "backup", f"Expected 'backup' key info, got: {key_info}"
    print(f"   [OK] Key info: {key_info['name']} ({key_info['type']})")
    
    print("\n6. Testing get_user_summary()...")
    summary = api_key_manager.get_user_summary(test_user_id)
    assert summary["has_keys"] == True, "Should have keys"
    assert summary["total_keys"] == 2, "Should have 2 keys"
    assert summary["selected_key_name"] == "backup", "Selected key should be 'backup'"
    print(f"   [OK] Summary: {summary['total_keys']} keys, selected: {summary['selected_key_name']}")
    
    print("\n7. Testing remove_key()...")
    result = api_key_manager.remove_key(test_user_id, "primary")
    assert result == True, "Failed to remove 'primary' key"
    
    keys = api_key_manager.list_keys(test_user_id)
    assert len(keys) == 1, f"Should have 1 key after removal, got {len(keys)}"
    assert keys[0]["name"] == "backup", "Remaining key should be 'backup'"
    print("   [OK] Removed 'primary' key, 'backup' remains")
    
    # Check that selection updated
    selected_info = api_key_manager.get_selected_key_info(test_user_id)
    assert selected_info["name"] == "backup", "Should still have 'backup' selected"
    
    print("\n8. Testing remove last key...")
    result = api_key_manager.remove_key(test_user_id, "backup")
    assert result == True, "Failed to remove last key"
    
    keys = api_key_manager.list_keys(test_user_id)
    assert len(keys) == 0, f"Should have 0 keys after removing all, got {len(keys)}"
    
    summary = api_key_manager.get_user_summary(test_user_id)
    assert summary["has_keys"] == False, "Should have no keys"
    assert summary["selected_key_name"] is None, "Selected key should be None"
    print("   [OK] Removed all keys, user has no keys")
    
    # Clean up
    if test_user_id in api_key_manager.data:
        del api_key_manager.data[test_user_id]
        api_key_manager._save_data()
    
    print("\n[PASS] All basic tests passed!")

def test_storage_persistence():
    """Test that data persists between instances"""
    print("\nTesting storage persistence...")
    
    test_user_id = 999888777
    test_key_name = "persistent_test"
    test_key_value = "sk-or-v1-persist123"
    
    # First, completely clean up any existing test data from file
    # by removing from global instance and saving
    user_key = str(test_user_id)
    if user_key in api_key_manager.data:
        del api_key_manager.data[user_key]
        api_key_manager._save_data()
    
    # Now add fresh test data
    api_key_manager.add_key(test_user_id, test_key_name, test_key_value, "openrouter")
    
    # Force save to file
    api_key_manager._save_data()
    
    print("   [OK] Saved data to file")
    
    # Create a completely new instance to test persistence
    from bot.api_key_manager import APIKeyManager
    new_manager = APIKeyManager()
    
    # Check if data loaded
    keys = new_manager.list_keys(test_user_id)
    assert len(keys) == 1, f"New instance should have 1 key, got {len(keys)}"
    assert keys[0]["name"] == test_key_name, f"Key name mismatch"
    assert keys[0]["key"] == test_key_value, f"Key value mismatch"
    
    print("   [OK] Data persisted to new instance")
    
    # Clean up from new instance
    if user_key in new_manager.data:
        del new_manager.data[user_key]
        new_manager._save_data()
    
    # Also clean up from global instance
    if user_key in api_key_manager.data:
        del api_key_manager.data[user_key]
        api_key_manager._save_data()
    
    print("   [OK] Cleaned up test data")
    
    print("\n[PASS] Storage persistence test passed!")

def test_integration_with_telegram_bot():
    """Test integration with Telegram bot components"""
    print("\nTesting integration with Telegram bot...")
    
    # Import the bot module to ensure no import errors
    try:
        from bot.telegram_bot import apikey_command, handle_project_request
        print("   [OK] Telegram bot imports successfully")
    except ImportError as e:
        print(f"   [WARNING] Import warning: {e}")
    
    # Test that api_key_manager is accessible
    from bot.telegram_bot import api_key_manager as bot_api_manager
    assert bot_api_manager is not None, "api_key_manager should be accessible in bot module"
    print("   [OK] api_key_manager accessible in bot module")
    
    print("\n[PASS] Integration tests passed!")

if __name__ == "__main__":
    print("=" * 60)
    print("API Key Manager Test Suite")
    print("=" * 60)
    
    try:
        test_basic_functionality()
        test_storage_persistence()
        test_integration_with_telegram_bot()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)
        
        # Show storage file location
        storage_file = api_key_manager.storage_file
        if os.path.exists(storage_file):
            print(f"\nStorage file: {os.path.abspath(storage_file)}")
            with open(storage_file, 'r') as f:
                content = f.read()
                print(f"   Size: {len(content)} bytes")
        
    except AssertionError as e:
        print(f"\n[FAILED] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)