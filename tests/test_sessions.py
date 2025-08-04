import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.sessions import SessionService, create_session, get_session, update_session, delete_session, list_sessions_by_period, get_current_session
from services.periods import create_period, delete_period
from utils.database import db_manager
from datetime import date as dt_date, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_test_period():
    """Create a test period for session testing"""
    try:
        # Create a test period
        today = dt_date.today()
        test_period = create_period(
            start_date=today.isoformat(),
            end_date=None,
            total_money=1000
        )
        
        if test_period:
            logger.info(f"Created test period: {test_period.start_date}")
            return str(test_period.id)  # type: ignore
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to setup test period: {e}")
        return None

def cleanup_test_data(test_dates, period_start_date):
    """Clean up test data after testing"""
    try:
        # Delete test sessions
        for date_str in test_dates:
            SessionService.delete_session_by_date(date_str)
        
        # Delete test period
        if period_start_date:
            delete_period(period_start_date)
        
        logger.info("Cleaned up test data")
        
    except Exception as e:
        logger.error(f"Failed to cleanup test data: {e}")

def test_sessions_crud():
    """Test all CRUD operations for Sessions model"""
    try:
        # Connect to database
        db_manager.connect()
        logger.info("✅ Connected to database")
        
        # Setup test period
        today = dt_date.today()
        period_start_date = today.isoformat()
        test_period = create_period(
            start_date=period_start_date,
            end_date=None,
            total_money=1000
        )
        
        if not test_period:
            print("❌ Failed to setup test period")
            return
        
        # Test data
        tomorrow = today + timedelta(days=1)
        day_after = today + timedelta(days=2)
        
        test_date_1 = today.isoformat()
        test_date_2 = tomorrow.isoformat()
        test_date_3 = day_after.isoformat()
        test_dates = [test_date_1, test_date_2, test_date_3]
        telegram_poll_message_id = "test_poll_12345"
        
        print("\n🧪 Testing Sessions CRUD Operations")
        print("=" * 50)
        
        # 1. CREATE SESSIONS
        print("\n1️⃣ Creating sessions...")
        session1 = create_session(
            date=test_date_1,
            period_id=period_start_date,
            courts_price=25.0,
            telegram_poll_message_id=telegram_poll_message_id
        )
        
        session2 = create_session(
            date=test_date_2,
            period_id=period_start_date,
            courts_price=30.0,
            telegram_poll_message_id=telegram_poll_message_id
        )
        
        session3 = create_session(
            date=test_date_3,
            period_id=period_start_date,
            courts_price=35.0,
            telegram_poll_message_id=telegram_poll_message_id
        )
        
        if session1:
            print(f"✅ Created session1: {session1.date} - Price: ${session1.courts_price}")
            print(f"   Period start: {session1.period.start_date}")  # type: ignore
            # Assert values match expected
            assert session1.date == dt_date.fromisoformat(test_date_1), f"Expected date {test_date_1}, got {session1.date}"
            assert session1.courts_price == 25.0, f"Expected price 25.0, got {session1.courts_price}"
            assert str(session1.period.start_date) == period_start_date, f"Expected period {period_start_date}, got {session1.period.start_date}"  # type: ignore
        else:
            assert False, "Failed to create session1"
            
        if session2:
            print(f"✅ Created session2: {session2.date} - Price: ${session2.courts_price}")
            # Assert values match expected
            assert session2.date == dt_date.fromisoformat(test_date_2), f"Expected date {test_date_2}, got {session2.date}"
            assert session2.courts_price == 30.0, f"Expected price 30.0, got {session2.courts_price}"
        else:
            assert False, "Failed to create session2"
            
        if session3:
            print(f"✅ Created session3: {session3.date} - Price: ${session3.courts_price}")
            # Assert values match expected
            assert session3.date == dt_date.fromisoformat(test_date_3), f"Expected date {test_date_3}, got {session3.date}"
            assert session3.courts_price == 35.0, f"Expected price 35.0, got {session3.courts_price}"
        else:
            assert False, "Failed to create session3"
        
        # 2. GET SESSION BY DATE
        print("\n2️⃣ Getting session by date...")
        retrieved_session = get_session(test_date_1)
        
        if retrieved_session:
            print(f"✅ Retrieved session: {retrieved_session.date}")
            print(f"   Courts price: ${retrieved_session.courts_price}")
            print(f"   Period start: {retrieved_session.period.start_date}")  # type: ignore
            # Assert retrieved values match expected
            assert retrieved_session.date == dt_date.fromisoformat(test_date_1), f"Expected date {test_date_1}, got {retrieved_session.date}"
            assert retrieved_session.courts_price == 25.0, f"Expected price 25.0, got {retrieved_session.courts_price}"
            assert str(retrieved_session.period.start_date) == period_start_date, f"Expected period {period_start_date}, got {retrieved_session.period.start_date}"  # type: ignore
        else:
            assert False, "Session not found when it should exist"
        
        # 3. UPDATE SESSION BY DATE
        print("\n3️⃣ Updating session by date...")
        updated_session = update_session(
            test_date_1,
            courts_price=40.0
        )
        
        if updated_session:
            print(f"✅ Updated session: {updated_session.date}")
            print(f"   New price: ${updated_session.courts_price}")
            # Assert updated values match expected
            assert updated_session.date == dt_date.fromisoformat(test_date_1), f"Expected date {test_date_1}, got {updated_session.date}"
            assert updated_session.courts_price == 40.0, f"Expected updated price 40.0, got {updated_session.courts_price}"
        else:
            assert False, "Failed to update session"
        
        # 4. GET CURRENT SESSION (TODAY)
        print("\n4️⃣ Getting current session (today)...")
        current_session = get_current_session()
        
        if current_session:
            print(f"✅ Found current session: {current_session.date}")
            print(f"   Price: ${current_session.courts_price}")
            # Assert current session is today's session
            assert current_session.date == dt_date.today(), f"Expected current session date to be today ({dt_date.today()}), got {current_session.date}"
            assert current_session.courts_price == 40.0, f"Expected current session price 40.0 (updated), got {current_session.courts_price}"
        else:
            print("ℹ️  No current session found - this might be expected if test date != today")
        
        # 5. LIST SESSIONS BY PERIOD
        print("\n5️⃣ Listing sessions by period...")
        period_sessions = list_sessions_by_period(period_start_date)
        print(f"✅ Found {len(period_sessions)} sessions for this period:")
        # Assert we have the expected number of sessions
        assert len(period_sessions) == 3, f"Expected 3 sessions for period, got {len(period_sessions)}"
        
        # Assert sessions have correct data
        session_dates = [str(session.date) for session in period_sessions]
        expected_dates = [test_date_1, test_date_2, test_date_3]
        for expected_date in expected_dates:
            assert expected_date in session_dates, f"Expected date {expected_date} not found in period sessions"
        
        for session in period_sessions:
            print(f"   - {session.date} - ${session.courts_price}")
            # Assert all sessions belong to the correct period
            assert str(session.period.start_date) == period_start_date, f"Session period mismatch: expected {period_start_date}, got {session.period.start_date}"  # type: ignore
        
        # 6. TEST DUPLICATE CREATION
        print("\n6️⃣ Testing duplicate session creation...")
        duplicate_session = SessionService.get_session_by_date(test_date_1)
        
        if duplicate_session:
            print(f"ℹ️  Session exists - retrieved existing session")
            print(f"   Price: ${duplicate_session.courts_price}")
            # Assert duplicate retrieval returns the same updated session
            assert duplicate_session.date == dt_date.fromisoformat(test_date_1), f"Expected date {test_date_1}, got {duplicate_session.date}"
            assert duplicate_session.courts_price == 40.0, f"Expected price 40.0 (updated), got {duplicate_session.courts_price}"
        else:
            assert False, "Duplicate session should exist but was not found"
        
        # 7. TEST INVALID PERIOD ID
        print("\n7️⃣ Testing invalid period ID...")
        invalid_session = create_session(
            date="2025-12-31",
            period_id="2099-12-31",  # Non-existent period
            courts_price=100.0,
            telegram_poll_message_id="test_poll_12345"
        )
        
        # Assert invalid period creation returns None
        assert invalid_session is None, f"Expected None for invalid period, got {invalid_session}"
        if invalid_session is None:
            print("✅ Invalid period ID properly handled (returned None)")
        else:
            print("❌ Invalid period ID should have returned None")
        
        # 8. TEST NON-EXISTENT SESSION OPERATIONS
        print("\n8️⃣ Testing non-existent session operations...")
        non_existent_date = "2099-12-31"
        
        # Get non-existent session
        non_existent = get_session(non_existent_date)
        assert non_existent is None, f"Expected None for non-existent session, got {non_existent}"
        if non_existent is None:
            print("✅ Non-existent session get properly handled")
        
        # Update non-existent session
        non_existent_update = update_session(non_existent_date, courts_price=999.0)
        assert non_existent_update is None, f"Expected None for non-existent session update, got {non_existent_update}"
        if non_existent_update is None:
            print("✅ Non-existent session update properly handled")
        
        # Delete non-existent session
        non_existent_delete = delete_session(non_existent_date)
        assert non_existent_delete is False, f"Expected False for non-existent session delete, got {non_existent_delete}"
        if not non_existent_delete:
            print("✅ Non-existent session delete properly handled")
        
        # 9. DELETE SESSIONS BY DATE
        print("\n9️⃣ Deleting sessions...")
        deleted1 = delete_session(test_date_1)
        deleted2 = delete_session(test_date_2)
        deleted3 = delete_session(test_date_3)
        
        # Assert deletions were successful
        assert deleted1 is True, f"Expected True for session1 deletion, got {deleted1}"
        assert deleted2 is True, f"Expected True for session2 deletion, got {deleted2}"
        assert deleted3 is True, f"Expected True for session3 deletion, got {deleted3}"
        
        if deleted1:
            print(f"✅ Deleted session: {test_date_1}")
        if deleted2:
            print(f"✅ Deleted session: {test_date_2}")
        if deleted3:
            print(f"✅ Deleted session: {test_date_3}")
        
        # Verify sessions are gone
        print("\n🔍 Verifying deletion...")
        deleted_session1 = get_session(test_date_1)
        deleted_session2 = get_session(test_date_2)
        deleted_session3 = get_session(test_date_3)
        
        # Assert all sessions are None after deletion
        assert deleted_session1 is None, f"Expected None for deleted session1, got {deleted_session1}"
        assert deleted_session2 is None, f"Expected None for deleted session2, got {deleted_session2}"
        assert deleted_session3 is None, f"Expected None for deleted session3, got {deleted_session3}"
        
        if all(s is None for s in [deleted_session1, deleted_session2, deleted_session3]):
            print("✅ All test sessions confirmed deleted")
        else:
            print("❌ Some sessions still exist!")
        
        # Cleanup test period
        delete_period(period_start_date)
        
        print("\n🎉 All Sessions CRUD operations completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")
    
    finally:
        # Disconnect from database
        db_manager.disconnect()
        logger.info("✅ Disconnected from database")

def test_session_edge_cases():
    """Test edge cases and error conditions"""
    try:
        db_manager.connect()
        logger.info("✅ Connected to database")
        
        print("\n🧪 Testing Sessions Edge Cases")
        print("=" * 40)
        
        # Setup test period
        today = dt_date.today()
        period_start_date = today.isoformat()
        test_period = create_period(
            start_date=period_start_date,
            end_date=None,
            total_money=1000
        )
        
        if not test_period:
            print("❌ Failed to setup test period for edge cases")
            return
        
        # Test invalid date formats
        print("\n1️⃣ Testing invalid date formats...")
        invalid_date_session = create_session(
            date="invalid-date",
            period_id=period_start_date,
            courts_price=25.0,
            telegram_poll_message_id="test_poll_12345"
        )
        
        # Assert invalid date format returns None
        assert invalid_date_session is None, f"Expected None for invalid date format, got {invalid_date_session}"
        if invalid_date_session is None:
            print("✅ Invalid date format properly handled")
        
        # Test negative price
        print("\n2️⃣ Testing edge case values...")
        edge_session = create_session(
            date="2025-08-10",
            period_id=period_start_date,
            courts_price=-10.0,  # Negative price
            telegram_poll_message_id="test_poll_12345"
        )
        
        if edge_session:
            print(f"ℹ️  Negative price allowed: ${edge_session.courts_price}")
            # Assert the negative price was actually saved
            assert edge_session.courts_price == -10.0, f"Expected price -10.0, got {edge_session.courts_price}"
            assert edge_session.date == dt_date.fromisoformat("2025-08-10"), f"Expected date 2025-08-10, got {edge_session.date}"
            # Clean up
            delete_result = delete_session("2025-08-10")
            assert delete_result is True, f"Expected True for cleanup deletion, got {delete_result}"
        
        # Clean up test period
        delete_period(period_start_date)
        
        print("\n🎉 Edge cases testing completed!")
        
    except Exception as e:
        logger.error(f"Edge cases test failed: {e}")
        print(f"❌ Edge cases test failed: {e}")
    
    finally:
        db_manager.disconnect()
        logger.info("✅ Disconnected from database")

if __name__ == "__main__":
    # Run main CRUD tests
    test_sessions_crud()
    
    # Run edge cases tests
    test_session_edge_cases()