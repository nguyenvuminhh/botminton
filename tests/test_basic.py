import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.users import create_user, get_user, delete_user
from services.periods import create_period, get_period, delete_period
from services.sessions import create_session, get_session, delete_session
from utils.database import db_manager
from datetime import date as dt_date
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_functionality():
    """Test basic functionality of all services"""
    try:
        # Connect to database
        db_manager.connect()
        print("✅ Connected to database")
        
        # Test data
        today = dt_date.today()
        test_date = today.isoformat()
        
        # 1. Test Users
        print("\n1️⃣ Testing Users...")
        user = create_user("test_user_123", "testuser")
        if user:
            print(f"✅ Created user: {user.telegram_id}")
            
            retrieved_user = get_user("test_user_123")
            if retrieved_user:
                print(f"✅ Retrieved user: {retrieved_user.telegram_user_name}")
            
            # Don't delete user yet, we need it for period money
        
        # 2. Test Periods
        print("\n2️⃣ Testing Periods...")
        period = create_period(test_date, None, 1000)
        if period:
            print(f"✅ Created period: {period.start_date}")
            
            retrieved_period = get_period(test_date)
            if retrieved_period:
                print(f"✅ Retrieved period: {retrieved_period.start_date}")
        
        # 3. Test Sessions
        print("\n3️⃣ Testing Sessions...")
        session = create_session(date=test_date, period_id=test_date, slots=6.0)
        if session:
            print(f"✅ Created session: {session.date}")
            
            retrieved_session = get_session(test_date)
            if retrieved_session:
                print(f"✅ Retrieved session: {retrieved_session.date}")
        
        # Cleanup
        print("\n🧹 Cleaning up...")
        delete_session(test_date)
        delete_period(test_date)
        delete_user("test_user_123")
        print("✅ Cleanup completed")
        
        print("\n🎉 Basic functionality test completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")
    
    finally:
        db_manager.disconnect()
        print("✅ Disconnected from database")

if __name__ == "__main__":
    test_basic_functionality()
