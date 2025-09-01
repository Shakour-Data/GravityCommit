#!/usr/bin/env python3
"""
Test script to verify scheduler functionality
"""

import time
from autocommit.scheduler import Scheduler

def test_scheduler():
    """Test the Scheduler class functionality"""

    print("Testing Scheduler functionality:")
    print("=" * 50)

    # Flag to check callback execution
    callback_executed = {'count': 0}

    def callback():
        print("✓ Scheduler callback executed")
        callback_executed['count'] += 1

    # Create scheduler with short interval (0.1 minutes = 6 seconds)
    scheduler = Scheduler(interval_minutes=0.1)

    # Start scheduler with callback
    scheduler.start(callback)

    # Wait for 7 seconds to allow callback to be called at least once
    time.sleep(7)

    # Stop scheduler
    scheduler.stop()

    # Check if callback was executed at least once
    assert callback_executed['count'] >= 1, "Scheduler callback was not executed"

    print(f"✓ Scheduler callback executed {callback_executed['count']} time(s)")

    print("\n✓ All Scheduler tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_scheduler()
        print("\n🎉 Scheduler module testing completed successfully!")
    except Exception as e:
        print(f"\n❌ Scheduler testing failed: {e}")
        exit(1)
