#!/usr/bin/env python3
"""
Test script for activity log API endpoints.
Make sure your backend server is running: uvicorn backend.app.main:app --reload
"""
import requests
import json
import sys

API_URL = "http://localhost:8000"
session = requests.Session()

def test_activity_api():
    """Test the activity log API endpoints."""
    print("Testing Activity Log API Endpoints")
    print("=" * 50)
    print("")
    
    # First, we need to login
    print("1. Logging in...")
    login_data = {
        "email": "test@example.com",  # Update with your test user email
        "password": "testpassword"      # Update with your test user password
    }
    
    login_response = session.post(
        f"{API_URL}/auth/login",
        json=login_data
    )
    
    if login_response.status_code != 200:
        print(f"   ERROR: Login failed (Status: {login_response.status_code})")
        print(f"   Response: {login_response.text}")
        print("   Please update email/password in this script or create a test user.")
        return False
    
    print("   Login successful")
    print("")
    
    # Test 2: Get all activity logs
    print("2. Getting all activity logs...")
    response = session.get(f"{API_URL}/activity/logs?page=1&page_size=10")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {data['total']} total logs, showing {len(data['logs'])} on page {data['page']}")
        if data['logs']:
            print(f"   First log: {data['logs'][0]['action']} at {data['logs'][0]['created_at']}")
        else:
            print("   No logs found. Run test_activity_logging.py to create some test logs.")
    else:
        print(f"   ERROR: Status {response.status_code}")
        print(f"   Response: {response.text}")
    print("")
    
    # Test 3: Get my activity logs
    print("3. Getting my activity logs...")
    response = session.get(f"{API_URL}/activity/logs/me?page=1&page_size=10")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {data['total']} of my logs")
        if data['logs']:
            for log in data['logs'][:3]:  # Show first 3
                print(f"     - {log['action']} at {log['created_at']}")
    else:
        print(f"   ERROR: Status {response.status_code}")
        print(f"   Response: {response.text}")
    print("")
    
    # Test 4: Get logs filtered by action
    print("4. Getting logs filtered by action (user.login)...")
    response = session.get(f"{API_URL}/activity/logs?action=user.login&page=1&page_size=10")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {data['total']} logs with action 'user.login'")
    else:
        print(f"   ERROR: Status {response.status_code}")
        print(f"   Response: {response.text}")
    print("")
    
    # Test 5: Get a specific log (if we have any)
    print("5. Getting a specific log (ID: 1)...")
    response = session.get(f"{API_URL}/activity/logs/1")
    if response.status_code == 200:
        log = response.json()
        print(f"   Log ID: {log['id']}")
        print(f"   Action: {log['action']}")
        print(f"   User: {log.get('user_name', 'N/A')} (ID: {log.get('user_id', 'N/A')})")
        print(f"   Created: {log['created_at']}")
    elif response.status_code == 404:
        print("   Log not found (this is OK if no logs exist)")
    else:
        print(f"   ERROR: Status {response.status_code}")
        print(f"   Response: {response.text}")
    print("")
    
    # Test 6: Test pagination
    print("6. Testing pagination (page 1, size 5)...")
    response = session.get(f"{API_URL}/activity/logs?page=1&page_size=5")
    if response.status_code == 200:
        data = response.json()
        print(f"   Page: {data['page']}, Page Size: {data['page_size']}")
        print(f"   Total: {data['total']}, Showing: {len(data['logs'])}")
    print("")
    
    print("=" * 50)
    print("Tests completed!")
    print("")
    print("Note: If you see empty results, create some activity logs first:")
    print("  python test_activity_logging.py")
    
    return True

if __name__ == "__main__":
    try:
        test_activity_api()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API server.")
        print("Make sure the backend server is running:")
        print("  uvicorn backend.app.main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

