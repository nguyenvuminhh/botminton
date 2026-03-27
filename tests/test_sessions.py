import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.sessions import SessionService, create_session, get_session, update_session, delete_session, list_sessions_by_period, get_current_session, get_open_session
from services.periods import create_period, delete_period
from utils.database import db_manager
from datetime import date as dt_date, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_sessions_crud():
    """Test all CRUD operations for Sessions model"""
    try:
        db_manager.connect()
        logger.info("✅ Connected to database")

        today = dt_date.today()
        period_start_date = today.isoformat()
        test_period = create_period(start_date=period_start_date, end_date=None, total_money=1000)

        if not test_period:
            print("❌ Failed to setup test period")
            return

        tomorrow = today + timedelta(days=1)
        day_after = today + timedelta(days=2)
        test_date_1 = today.isoformat()
        test_date_2 = tomorrow.isoformat()
        test_date_3 = day_after.isoformat()
        test_dates = [test_date_1, test_date_2, test_date_3]

        print("\n🧪 Testing Sessions CRUD Operations")
        print("=" * 50)

        # 1. CREATE
        print("\n1️⃣ Creating sessions...")
        session1 = create_session(date=test_date_1, period_id=period_start_date, slots=6.0)
        session2 = create_session(date=test_date_2, period_id=period_start_date, slots=4.0)
        session3 = create_session(date=test_date_3, period_id=period_start_date, slots=8.0)

        assert session1, "Failed to create session1"
        assert session2, "Failed to create session2"
        assert session3, "Failed to create session3"
        assert session1.date == dt_date.fromisoformat(test_date_1)
        assert session1.slots == 6.0
        assert str(session1.period.start_date) == period_start_date  # type: ignore
        print(f"✅ Created sessions: {test_date_1}, {test_date_2}, {test_date_3}")

        # 2. GET
        print("\n2️⃣ Getting session by date...")
        retrieved = get_session(test_date_1)
        assert retrieved is not None, "Session not found"
        assert retrieved.date == dt_date.fromisoformat(test_date_1)
        assert retrieved.slots == 6.0
        print(f"✅ Retrieved session: {retrieved.date}, slots={retrieved.slots}")

        # 3. UPDATE slots
        print("\n3️⃣ Updating session slots...")
        updated = update_session(test_date_1, slots=9.0)
        assert updated is not None, "Failed to update session"
        assert updated.slots == 9.0
        print(f"✅ Updated slots to {updated.slots}")

        # 4. UPDATE is_poll_open
        print("\n4️⃣ Testing poll open flag...")
        update_session(test_date_1, is_poll_open=True, telegram_poll_message_id="999")
        open_session = get_open_session()
        assert open_session is not None, "Expected open session"
        assert str(open_session.date) == test_date_1
        update_session(test_date_1, is_poll_open=False)
        print("✅ Poll open/close flag works")

        # 5. GET CURRENT SESSION
        print("\n5️⃣ Getting current session (today)...")
        current = get_current_session()
        if current:
            assert current.date == dt_date.today()
            print(f"✅ Current session: {current.date}")
        else:
            print("ℹ️  No current session found (expected if date mismatch)")

        # 6. LIST BY PERIOD
        print("\n6️⃣ Listing sessions by period...")
        period_sessions = list_sessions_by_period(period_start_date)
        assert len(period_sessions) == 3, f"Expected 3, got {len(period_sessions)}"
        print(f"✅ Found {len(period_sessions)} sessions in period")

        # 7. INVALID PERIOD
        print("\n7️⃣ Testing invalid period ID...")
        invalid = create_session(date="2025-12-31", period_id="2099-12-31")
        assert invalid is None, "Expected None for invalid period"
        print("✅ Invalid period handled")

        # 8. NON-EXISTENT SESSION OPS
        print("\n8️⃣ Non-existent session operations...")
        assert get_session("2099-12-31") is None
        assert update_session("2099-12-31", slots=5.0) is None
        assert delete_session("2099-12-31") is False
        print("✅ Non-existent operations handled")

        # 9. DELETE
        print("\n9️⃣ Deleting sessions...")
        assert delete_session(test_date_1) is True
        assert delete_session(test_date_2) is True
        assert delete_session(test_date_3) is True
        assert all(get_session(d) is None for d in test_dates)
        print("✅ All sessions deleted")

        delete_period(period_start_date)
        print("\n🎉 All Sessions CRUD operations completed successfully!")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")
        raise
    finally:
        db_manager.disconnect()


def test_session_edge_cases():
    """Test edge cases and error conditions"""
    try:
        db_manager.connect()

        today = dt_date.today()
        period_start_date = today.isoformat()
        test_period = create_period(start_date=period_start_date)
        if not test_period:
            print("❌ Failed to setup test period for edge cases")
            return

        print("\n🧪 Testing Sessions Edge Cases")
        print("=" * 40)

        # Invalid date
        invalid = create_session(date="invalid-date", period_id=period_start_date)
        assert invalid is None
        print("✅ Invalid date handled")

        # Zero slots (allowed)
        edge = create_session(date="2025-08-10", period_id=period_start_date, slots=0.0)
        if edge:
            assert edge.slots == 0.0
            delete_session("2025-08-10")
            print("✅ Zero slots allowed")

        delete_period(period_start_date)
        print("\n🎉 Edge cases completed!")

    except Exception as e:
        logger.error(f"Edge cases test failed: {e}")
        print(f"❌ Edge cases test failed: {e}")
        raise
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    test_sessions_crud()
    test_session_edge_cases()
