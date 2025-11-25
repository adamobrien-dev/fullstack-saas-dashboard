#!/usr/bin/env python3
"""
Test script for activity logging utility.
Run this from the project root: python test_activity_logging.py
"""
import sys
from backend.app.db.session import SessionLocal
from backend.app.utils.activity import log_activity, ActivityAction, ResourceType
from backend.app.models.activity import ActivityLog
from sqlalchemy import select

def test_activity_logging():
    """Test the activity logging utility functions."""
    db = SessionLocal()
    
    try:
        print(" Testing Activity Logging Utility\n")
        
        # Test 1: Basic activity log
        print("1. Creating a basic activity log...")
        log1 = log_activity(
            db=db,
            action=ActivityAction.USER_LOGIN,
            user_id=1,  # Assuming user ID 1 exists
            resource_type=ResourceType.USER,
            resource_id=1,
            details={"method": "email", "success": True},
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Test Browser)"
        )
        print(f"   Created log ID: {log1.id}")
        print(f"   Action: {log1.action}")
        print(f"   User ID: {log1.user_id}")
        print(f"   Details: {log1.details}\n")
        
        # Test 2: Organization activity
        print("2. Creating an organization activity log...")
        log2 = log_activity(
            db=db,
            action=ActivityAction.ORG_CREATE,
            user_id=1,
            resource_type=ResourceType.ORGANIZATION,
            resource_id=1,
            organization_id=1,
            details={"name": "Test Organization", "created_by": "user@example.com"}
        )
        print(f"   Created log ID: {log2.id}")
        print(f"   Action: {log2.action}")
        print(f"   Organization ID: {log2.organization_id}\n")
        
        # Test 3: Query recent logs
        print("3. Querying recent activity logs...")
        recent_logs = db.execute(
            select(ActivityLog)
            .order_by(ActivityLog.created_at.desc())
            .limit(5)
        ).scalars().all()
        
        print(f"   Found {len(recent_logs)} recent logs:")
        for log in recent_logs:
            print(f"     - [{log.created_at}] {log.action} by user {log.user_id}")
        
        print("\nAll tests passed!")
        print("\nTip: Check the database to see all logs:")
        print("   SELECT * FROM activity_logs ORDER BY created_at DESC;")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    test_activity_logging()

