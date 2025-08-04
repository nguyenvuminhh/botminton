import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.period_moneys import (
    create_period_money, mark_as_paid_by_telegram_id, mark_as_unpaid_by_telegram_id,
    list_paid_by_period_start_date, list_unpaid_by_period_start_date
)
from services.periods import create_period, delete_period
from services.users import create_user, delete_user
from utils.database import db_manager
from datetime import date as dt_date
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_period_money_payment_status():
    """Test payment status functions for PeriodMoneys"""
    user_telegram_id = "test_user_123"
    today = dt_date.today().isoformat()

    try:
        # Connect to database
        db_manager.connect()
        logger.info("✅ Connected to database")
        
        # Setup test data
        
        # Create test user
        user = create_user(user_telegram_id, "testuser")
        assert user, "Failed to create test user"
        
        # Create test period
        period = create_period(today, None, 1000)
        assert period, "Failed to create test period"
        
        # Create period money
        period_money = create_period_money(today, user_telegram_id, 500.0)
        assert period_money, "Failed to create period money"
        
        # 1. Mark as Paid
        print("\n1️⃣ Marking period money as paid...")
        paid_pm = mark_as_paid_by_telegram_id(today, user_telegram_id)
        assert paid_pm and paid_pm.has_paid, "Failed to mark period money as paid"
        print(f"✅ Marked as paid: {paid_pm.has_paid}")
        
        # 2. Mark as Unpaid
        print("\n2️⃣ Marking period money as unpaid...")
        unpaid_pm = mark_as_unpaid_by_telegram_id(today, user_telegram_id)
        assert unpaid_pm and not unpaid_pm.has_paid, "Failed to mark period money as unpaid"
        print(f"✅ Marked as unpaid: {unpaid_pm.has_paid}")
        
        # 3. List Paid Period Moneys
        print("\n3️⃣ Listing paid period moneys...")
        paid_list = list_paid_by_period_start_date(today)
        assert len(paid_list) == 0, f"Expected 0 paid period moneys, found {len(paid_list)}"
        print("✅ No paid period moneys found (as expected)")
        
        # Mark as Paid again for testing
        mark_as_paid_by_telegram_id(today, user_telegram_id)
        
        # 4. List Unpaid Period Moneys
        print("\n4️⃣ Listing unpaid period moneys...")
        unpaid_list = list_unpaid_by_period_start_date(today)
        assert len(unpaid_list) == 0, f"Expected 0 unpaid period moneys, found {len(unpaid_list)}"
        print("✅ No unpaid period moneys found (as expected)")
        
        # Verify Paid List
        paid_list = list_paid_by_period_start_date(today)
        assert len(paid_list) == 1, f"Expected 1 paid period money, found {len(paid_list)}"
        print(f"✅ Found {len(paid_list)} paid period money")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")
    
    finally:
        # Cleanup test data
        delete_period(today)
        delete_user(user_telegram_id)
        db_manager.disconnect()
        logger.info("✅ Disconnected from database")

if __name__ == "__main__":
    test_period_money_payment_status()
