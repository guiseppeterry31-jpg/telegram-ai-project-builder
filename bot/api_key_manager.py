#!/usr/bin/env python3
"""API Key Manager for Telegram AI Project Builder Bot

Allows users to manage multiple OpenRouter API keys through Telegram.
Each user can add, list, select, remove, and test their API keys.
"""

import json
import os
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class APIKeyManager:
    """Manages API keys for users"""
    
    def __init__(self, storage_file: str = "user_api_keys.json"):
        self.storage_file = storage_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load API key data from storage file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Normalize keys to strings for consistency
                    # JSON loads keys as strings, but we ensure all are strings
                    normalized_data = {}
                    for key, value in data.items():
                        # Key should already be string from JSON, but ensure it
                        normalized_data[str(key)] = value
                    return normalized_data
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading API key data: {e}")
                return {}
        return {}
    
    def _get_user_key(self, user_id: int) -> str:
        """Convert user_id to string key for consistent storage"""
        return str(user_id)
    
    def _save_data(self):
        """Save API key data to storage file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            logger.error(f"Error saving API key data: {e}")
    
    def add_key(self, user_id: int, key_name: str, api_key: str, key_type: str = "openrouter") -> bool:
        """Add a new API key for a user"""
        user_key = self._get_user_key(user_id)
        
        if user_key not in self.data:
            self.data[user_key] = {
                "keys": [],
                "selected_key": None
            }
        
        # Check if key with same name already exists
        for key in self.data[user_key]["keys"]:
            if key["name"] == key_name:
                return False
        
        # Add the new key
        self.data[user_key]["keys"].append({
            "name": key_name,
            "key": api_key,
            "type": key_type
        })
        
        # If this is the first key, select it automatically
        if self.data[user_key]["selected_key"] is None:
            self.data[user_key]["selected_key"] = key_name
        
        self._save_data()
        return True
    
    def list_keys(self, user_id: int) -> List[Dict]:
        """List all API keys for a user"""
        user_key = self._get_user_key(user_id)
        if user_key not in self.data:
            return []
        return self.data[user_key]["keys"]
    
    def get_selected_key(self, user_id: int) -> Optional[str]:
        """Get the currently selected API key for a user"""
        user_key = self._get_user_key(user_id)
        if user_key not in self.data:
            return None
        
        selected_name = self.data[user_key].get("selected_key")
        if not selected_name:
            return None
        
        # Find the key with the selected name
        for key in self.data[user_key]["keys"]:
            if key["name"] == selected_name:
                return key["key"]
        
        return None
    
    def get_selected_key_info(self, user_id: int) -> Optional[Dict]:
        """Get info about the currently selected API key"""
        user_key = self._get_user_key(user_id)
        if user_key not in self.data:
            return None
        
        selected_name = self.data[user_key].get("selected_key")
        if not selected_name:
            return None
        
        # Find the key with the selected name
        for key in self.data[user_key]["keys"]:
            if key["name"] == selected_name:
                return key
        
        return None
    
    def select_key(self, user_id: int, key_name: str) -> bool:
        """Select an API key by name"""
        user_key = self._get_user_key(user_id)
        if user_key not in self.data:
            return False
        
        # Check if key exists
        key_exists = False
        for key in self.data[user_key]["keys"]:
            if key["name"] == key_name:
                key_exists = True
                break
        
        if not key_exists:
            return False
        
        self.data[user_key]["selected_key"] = key_name
        self._save_data()
        return True
    
    def remove_key(self, user_id: int, key_name: str) -> bool:
        """Remove an API key by name"""
        user_key = self._get_user_key(user_id)
        if user_key not in self.data:
            return False
        
        # Find and remove the key
        new_keys = []
        key_removed = False
        
        for key in self.data[user_key]["keys"]:
            if key["name"] != key_name:
                new_keys.append(key)
            else:
                key_removed = True
        
        if not key_removed:
            return False
        
        self.data[user_key]["keys"] = new_keys
        
        # If we removed the selected key, select another one if available
        if self.data[user_key].get("selected_key") == key_name:
            if new_keys:
                self.data[user_key]["selected_key"] = new_keys[0]["name"]
            else:
                self.data[user_key]["selected_key"] = None
        
        self._save_data()
        return True
    
    def test_key(self, user_id: int, key_name: Optional[str] = None) -> Dict[str, Any]:
        """Test an API key (or the selected one if none specified)"""
        from ai.openrouter import call_openrouter
        
        user_key = self._get_user_key(user_id)
        if user_key not in self.data or not self.data[user_key]["keys"]:
            return {"success": False, "message": "No API keys found"}
        
        # Find the key to test
        key_to_test = None
        if key_name:
            for key in self.data[user_key]["keys"]:
                if key["name"] == key_name:
                    key_to_test = key
                    break
        else:
            # Use selected key
            selected_info = self.get_selected_key_info(user_id)
            if selected_info:
                key_to_test = selected_info
        
        if not key_to_test:
            return {"success": False, "message": f"Key '{key_name}' not found"}
        
        # Test the key
        try:
            test_prompt = "Hello, please respond with 'TEST PASSED' if you can read this."
            response = call_openrouter(test_prompt, "openrouter/free", key_to_test["key"])
            
            if response and len(response) > 0:
                return {
                    "success": True,
                    "message": f"API key '{key_to_test['name']}' is working!",
                    "response_preview": response[:100]
                }
            else:
                return {
                    "success": False,
                    "message": f"API key '{key_to_test['name']}' returned empty response"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"API key '{key_to_test['name']}' test failed: {str(e)}"
            }
    
    def get_user_summary(self, user_id: int) -> Dict[str, Any]:
        """Get summary of user's API key status"""
        user_key = self._get_user_key(user_id)
        if user_key not in self.data:
            return {
                "has_keys": False,
                "total_keys": 0,
                "selected_key": None,
                "selected_key_name": None
            }
        
        keys = self.data[user_key]["keys"]
        selected_name = self.data[user_key].get("selected_key")
        selected_key = None
        
        if selected_name:
            for key in keys:
                if key["name"] == selected_name:
                    selected_key = key["key"][:10] + "..." + key["key"][-10:] if len(key["key"]) > 20 else key["key"]
                    break
        
        return {
            "has_keys": len(keys) > 0,
            "total_keys": len(keys),
            "selected_key": selected_key,
            "selected_key_name": selected_name
        }


# Global instance
api_key_manager = APIKeyManager()