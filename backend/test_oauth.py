#!/usr/bin/env python3
"""
Test script for Yahoo OAuth implementation
Run this after restarting the server to test the OAuth endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test basic health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_yahoo_auth_init():
    """Test Yahoo OAuth initiation"""
    print("Testing Yahoo OAuth initiation...")
    response = requests.get(f"{BASE_URL}/auth/yahoo")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Auth URL: {data.get('auth_url')}")
        print(f"State: {data.get('state')}")
        print("✅ OAuth initiation working!")
        return data.get('state')
    else:
        print(f"❌ Error: {response.text}")
        return None

def test_auth_status(state):
    """Test auth status endpoint"""
    if not state:
        print("Skipping auth status test - no state available")
        return
    
    print(f"Testing auth status for state: {state}")
    response = requests.get(f"{BASE_URL}/auth/status/{state}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def main():
    """Run all tests"""
    print("🚀 Testing Fantasy Draft Co-Pilot OAuth Implementation")
    print("=" * 60)
    
    # Test basic health
    test_health()
    
    # Test OAuth initiation
    state = test_yahoo_auth_init()
    
    # Test auth status
    test_auth_status(state)
    
    print("=" * 60)
    print("✅ Basic OAuth implementation tests complete!")
    print()
    print("Next steps:")
    print("1. Set up your Yahoo API credentials in .env file")
    print("2. Copy .env.example to .env and fill in your Yahoo Client ID and Secret")
    print("3. Test the full OAuth flow by visiting the auth_url")

if __name__ == "__main__":
    main()
