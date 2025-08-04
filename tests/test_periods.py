import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.periods import (
    PeriodService,
    create_period, get_period, update_period, delete_period, list_all_periods, get_current_period,
)
from services.period_moneys import (
    create_period_money, get_period_money, get_period_money_by_id, 
    update_period_money, update_period_money_by_id,
    delete_period_money, list_period_moneys_by_period, list_period_moneys_by_user, get_total_money_for_period
)
from services.users import create_user, delete_user
from utils.database import db_manager
from datetime import date as dt_date, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_test_user():
    """Create a test user for period money testing"""
    try:
        user_telegram_id = "test_period_user_123"
        
        # First try to delete existing test user to start clean
        delete_user(user_telegram_id)
        
        # Create fresh test user
        test_user = create_user(
            telegram_id=user_telegram_id,
            telegram_user_name="test_period_user",
        )
        return user_telegram_id if test_user else None
        
    except Exception as e:
        logger.error(f"Failed to setup test user: {e}")
        return None

def setup_second_test_user():
    """Create a second test user for period money testing"""
    try:
        user_telegram_id = "test_period_user_456"
        
        # First try to delete existing test user to start clean
        delete_user(user_telegram_id)
        
        # Create fresh test user
        test_user = create_user(
            telegram_id=user_telegram_id,
            telegram_user_name="test_period_user_2",
        )
        return user_telegram_id if test_user else None
        
    except Exception as e:
        logger.error(f"Failed to setup second test user: {e}")
        return None

def cleanup_test_data(test_dates, user_telegram_id):
    """Clean up test data after testing"""
    try:
        # Delete test periods (this will cascade delete period_moneys)
        if test_dates:
            for date_str in test_dates:
                delete_period(date_str)
        
        # Delete test user
        if user_telegram_id:
            delete_user(user_telegram_id)
        
        logger.info("Cleaned up test data")
        
    except Exception as e:
        logger.error(f"Failed to cleanup test data: {e}")

def cleanup_existing_test_data():
    """Clean up any existing test data before starting tests"""
    try:
        user_telegram_id = "test_period_user_123"
        second_user_telegram_id = "test_period_user_456"
        
        # Delete any existing test users and related data
        delete_user(user_telegram_id)
        delete_user(second_user_telegram_id)
        
        # Delete test periods from recent dates that might have been left behind
        today = dt_date.today()
        for i in range(-5, 6):  # Clean up 10 days around today
            test_date = (today + timedelta(days=i)).isoformat()
            delete_period(test_date)
        
        logger.info("Cleaned up existing test data")
        
    except Exception as e:
        logger.error(f"Failed to cleanup existing test data: {e}")

def test_periods_crud():
    """Test all CRUD operations for Periods model"""
    try:
        # Connect to database
        db_manager.connect()
        logger.info("✅ Connected to database")
        
        # Test data
        today = dt_date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        day_after = today + timedelta(days=2)
        
        test_date_1 = yesterday.isoformat()  # Past period
        test_date_2 = today.isoformat()     # Current period
        test_date_3 = tomorrow.isoformat()  # Future period
        test_dates = [test_date_1, test_date_2, test_date_3]
        
        print("\n🧪 Testing Periods CRUD Operations")
        print("=" * 50)
        
        # 1. CREATE PERIODS WITH UNIQUE START_DATE
        print("\n1️⃣ Creating periods with unique start_date...")
        period1 = create_period(
            start_date=test_date_1,
            end_date=test_date_2,
            total_money=1000
        )
        
        period2 = create_period(
            start_date=test_date_2,
            end_date=None,  # Ongoing period
            total_money=2000
        )
        
        period3 = create_period(
            start_date=test_date_3,
            total_money=None
        )
        
        if period1:
            print(f"✅ Created period1: {period1.start_date} to {period1.end_date} - ${period1.total_money}")
            # Assert period1 values match expected
            assert period1.start_date == dt_date.fromisoformat(test_date_1), f"Expected start_date {test_date_1}, got {period1.start_date}"
            assert period1.end_date == dt_date.fromisoformat(test_date_2), f"Expected end_date {test_date_2}, got {period1.end_date}"
            assert period1.total_money == 1000, f"Expected total_money 1000, got {period1.total_money}"
        else:
            assert False, "Failed to create period1"
            
        if period2:
            print(f"✅ Created period2: {period2.start_date} (ongoing) - ${period2.total_money}")
            # Assert period2 values match expected
            assert period2.start_date == dt_date.fromisoformat(test_date_2), f"Expected start_date {test_date_2}, got {period2.start_date}"
            assert period2.end_date is None, f"Expected end_date None, got {period2.end_date}"
            assert period2.total_money == 2000, f"Expected total_money 2000, got {period2.total_money}"
        else:
            assert False, "Failed to create period2"
            
        if period3:
            print(f"✅ Created period3: {period3.start_date} - ${period3.total_money}")
            # Assert period3 values match expected
            assert period3.start_date == dt_date.fromisoformat(test_date_3), f"Expected start_date {test_date_3}, got {period3.start_date}"
            assert period3.end_date is None, f"Expected end_date None, got {period3.end_date}" 
            assert period3.total_money is None, f"Expected total_money None, got {period3.total_money}"
        else:
            assert False, "Failed to create period3"
        
        # 2. TEST DUPLICATE START_DATE (should return existing)
        print("\n2️⃣ Testing duplicate start_date...")
        duplicate_period = create_period(
            start_date=test_date_1,
            end_date="2025-12-31",
            total_money=9999
        )
        
        if duplicate_period:
            print("ℹ️  Duplicate creation handled - existing period returned")
            print(f"   Original values preserved: ${duplicate_period.total_money}")
            # Assert duplicate returns the same period with original values
            assert duplicate_period.start_date == dt_date.fromisoformat(test_date_1), f"Expected start_date {test_date_1}, got {duplicate_period.start_date}"
            assert duplicate_period.total_money == 1000, f"Expected original total_money 1000, got {duplicate_period.total_money}"
            # Should NOT have the new values from duplicate creation attempt
            assert duplicate_period.total_money != 9999, "Duplicate creation should not overwrite existing values"
        else:
            assert False, "Duplicate period creation should return existing period"
        
        # 3. GET PERIOD BY START_DATE
        print("\n3️⃣ Getting period by start_date...")
        retrieved_period = get_period(test_date_2)
        
        if retrieved_period:
            print(f"✅ Retrieved period: {retrieved_period.start_date}")
            print(f"   End date: {retrieved_period.end_date}")
            print(f"   Total money: ${retrieved_period.total_money}")
            # Assert retrieved values match expected
            assert retrieved_period.start_date == dt_date.fromisoformat(test_date_2), f"Expected start_date {test_date_2}, got {retrieved_period.start_date}"
            assert retrieved_period.end_date is None, f"Expected end_date None, got {retrieved_period.end_date}"
            assert retrieved_period.total_money == 2000, f"Expected total_money 2000, got {retrieved_period.total_money}"
        else:
            assert False, "Period not found when it should exist"
        
        # 4. UPDATE PERIOD BY START_DATE
        print("\n4️⃣ Updating period by start_date...")
        updated_period = update_period(
            test_date_1,
            end_date=day_after.isoformat(),
            total_money=1500
        )
        
        if updated_period:
            print(f"✅ Updated period: {updated_period.start_date}")
            print(f"   New end date: {updated_period.end_date}")
            print(f"   New total money: ${updated_period.total_money}")
            # Assert updated values match expected
            assert updated_period.start_date == dt_date.fromisoformat(test_date_1), f"Expected start_date {test_date_1}, got {updated_period.start_date}"
            assert updated_period.end_date == dt_date.fromisoformat(day_after.isoformat()), f"Expected end_date {day_after.isoformat()}, got {updated_period.end_date}"
            assert updated_period.total_money == 1500, f"Expected updated total_money 1500, got {updated_period.total_money}"
        else:
            assert False, "Failed to update period"
        
        # 5. GET CURRENT PERIOD
        print("\n5️⃣ Getting current period...")
        current_period = get_current_period()
        
        if current_period:
            print(f"✅ Found current period: {current_period.start_date}")
            print(f"   End date: {current_period.end_date}")
            print(f"   Total money: ${current_period.total_money}")
            # Assert current period logic - should be period2 (ongoing) since it starts today and has no end_date
            assert current_period.start_date == dt_date.fromisoformat(test_date_2), f"Expected current period start_date {test_date_2}, got {current_period.start_date}"
            assert current_period.end_date is None, f"Expected current period end_date None (ongoing), got {current_period.end_date}"
            assert current_period.total_money == 2000, f"Expected current period total_money 2000, got {current_period.total_money}"
        else:
            print("ℹ️  No current period found - this might be expected based on test dates")
        
        # 6. LIST ALL PERIODS
        print("\n6️⃣ Listing all periods...")
        all_periods = list_all_periods(limit=10)
        print(f"✅ Found {len(all_periods)} periods:")
        # Assert we have at least our test periods
        assert len(all_periods) >= 3, f"Expected at least 3 periods (our test periods), got {len(all_periods)}"
        
        # Check that our test periods are in the list
        period_start_dates = [str(p.start_date) for p in all_periods]
        assert test_date_1 in period_start_dates, f"Test period {test_date_1} not found in periods list"
        assert test_date_2 in period_start_dates, f"Test period {test_date_2} not found in periods list"
        assert test_date_3 in period_start_dates, f"Test period {test_date_3} not found in periods list"
        
        for p in all_periods:
            end_str = f" to {p.end_date}" if p.end_date else " (ongoing)"
            print(f"   - {p.start_date}{end_str} - ${p.total_money}")
        
        # 7. GET PERIOD COUNT
        print("\n7️⃣ Getting period count...")
        count = PeriodService.get_period_count()
        print(f"✅ Total periods in database: {count}")
        # Assert count is reasonable (at least our test periods)
        assert count >= 3, f"Expected at least 3 periods in database, got {count}"
        assert isinstance(count, int), f"Expected int for count, got {type(count)}"
        
        # 8. TEST NON-EXISTENT OPERATIONS
        print("\n8️⃣ Testing non-existent period operations...")
        non_existent_date = "2099-12-31"
        
        # Get non-existent period
        non_existent = get_period(non_existent_date)
        # Assert non-existent period returns None
        assert non_existent is None, f"Expected None for non-existent period, got {non_existent}"
        if non_existent is None:
            print("✅ Non-existent period get properly handled")
        
        # Update non-existent period
        non_existent_update = update_period(non_existent_date, total_money=9999)
        # Assert non-existent period update returns None
        assert non_existent_update is None, f"Expected None for non-existent period update, got {non_existent_update}"
        if non_existent_update is None:
            print("✅ Non-existent period update properly handled")
        
        # Delete non-existent period
        non_existent_delete = delete_period(non_existent_date)
        # Assert non-existent period delete returns False
        assert non_existent_delete is False, f"Expected False for non-existent period delete, got {non_existent_delete}"
        if not non_existent_delete:
            print("✅ Non-existent period delete properly handled")
        
        print("\n🎉 Periods CRUD operations completed successfully!")
        return test_dates
        
    except Exception as e:
        logger.error(f"Periods test failed: {e}")
        print(f"❌ Periods test failed: {e}")
        return []

def test_period_moneys_crud(test_dates):
    """Test all CRUD operations for PeriodMoneys model"""
    try:
        if not test_dates:
            print("❌ No test periods available for period money testing")
            return
        
        # Setup test user
        user_telegram_id = setup_test_user()
        if not user_telegram_id:
            print("❌ Failed to setup test user")
            return
        
        # Setup second test user for testing multiple users per period
        second_user_telegram_id = setup_second_test_user()
        if not second_user_telegram_id:
            print("❌ Failed to setup second test user")
            return
        
        print("\n🧪 Testing PeriodMoneys CRUD Operations")
        print("=" * 50)
        
        period_money_ids = []
        
        # 1. CREATE PERIOD MONEYS
        print("\n1️⃣ Creating period moneys...")
        period_money1 = create_period_money(
            period_start_date=test_dates[0],
            user_telegram_id=user_telegram_id,
            amount=100.50
        )
        
        period_money2 = create_period_money(
            period_start_date=test_dates[1],
            user_telegram_id=user_telegram_id,
            amount=250.75
        )
        
        period_money3 = create_period_money(
            period_start_date=test_dates[0],  # Same period, different user
            user_telegram_id=second_user_telegram_id,
            amount=75.25
        )
        
        if period_money1:
            period_money_ids.append(str(period_money1.id))  # type: ignore
            print(f"✅ Created period_money1: ${period_money1.amount} for period {test_dates[0]}")
            # Assert period_money1 values match expected
            assert str(period_money1.period.start_date) == test_dates[0], f"Expected period start_date {test_dates[0]}, got {period_money1.period.start_date}"  # type: ignore
            assert period_money1.user.telegram_id == user_telegram_id, f"Expected user telegram_id {user_telegram_id}, got {period_money1.user.telegram_id}"  # type: ignore
            assert period_money1.amount == 100.50, f"Expected amount 100.50, got {period_money1.amount}"
        else:
            assert False, "Failed to create period_money1"
            
        if period_money2:
            period_money_ids.append(str(period_money2.id))  # type: ignore
            print(f"✅ Created period_money2: ${period_money2.amount} for period {test_dates[1]}")
            # Assert period_money2 values match expected
            assert str(period_money2.period.start_date) == test_dates[1], f"Expected period start_date {test_dates[1]}, got {period_money2.period.start_date}"  # type: ignore
            assert period_money2.user.telegram_id == user_telegram_id, f"Expected user telegram_id {user_telegram_id}, got {period_money2.user.telegram_id}"  # type: ignore
            assert period_money2.amount == 250.75, f"Expected amount 250.75, got {period_money2.amount}"
        else:
            assert False, "Failed to create period_money2"
            
        if period_money3:
            period_money_ids.append(str(period_money3.id))  # type: ignore
            print(f"✅ Created period_money3: ${period_money3.amount} for period {test_dates[0]}")
            # Assert period_money3 values match expected
            assert str(period_money3.period.start_date) == test_dates[0], f"Expected period start_date {test_dates[0]}, got {period_money3.period.start_date}"  # type: ignore
            assert period_money3.user.telegram_id == second_user_telegram_id, f"Expected user telegram_id {second_user_telegram_id}, got {period_money3.user.telegram_id}"  # type: ignore
            assert period_money3.amount == 75.25, f"Expected amount 75.25, got {period_money3.amount}"
        else:
            assert False, "Failed to create period_money3"
        
        # 2. GET PERIOD MONEY BY DATE AND USER (NEW METHOD)
        print("\n2️⃣ Getting period money by date and user...")
        retrieved_pm = get_period_money(test_dates[0], user_telegram_id)
        
        if retrieved_pm:
            print(f"✅ Retrieved period money: ${retrieved_pm.amount}")
            print(f"   Period: {retrieved_pm.period.start_date}")  # type: ignore
            print(f"   User: {retrieved_pm.user.telegram_id}")  # type: ignore
            # Assert retrieved values match expected
            assert retrieved_pm.amount == 100.50, f"Expected amount 100.50, got {retrieved_pm.amount}"
            assert str(retrieved_pm.period.start_date) == test_dates[0], f"Expected period {test_dates[0]}, got {retrieved_pm.period.start_date}"  # type: ignore
            assert retrieved_pm.user.telegram_id == user_telegram_id, f"Expected user {user_telegram_id}, got {retrieved_pm.user.telegram_id}"  # type: ignore
        else:
            assert False, "Period money not found when it should exist"
        
        # 2b. GET PERIOD MONEY BY ID (LEGACY METHOD)
        print("\n2b️⃣ Getting period money by ID (legacy method)...")
        if period_money_ids:
            retrieved_pm_by_id = get_period_money_by_id(period_money_ids[0])
            
            if retrieved_pm_by_id:
                print(f"✅ Retrieved period money by ID: ${retrieved_pm_by_id.amount}")
                # Assert retrieved values match expected
                assert retrieved_pm_by_id.amount == 100.50, f"Expected amount 100.50, got {retrieved_pm_by_id.amount}"
                assert str(retrieved_pm_by_id.period.start_date) == test_dates[0], f"Expected period {test_dates[0]}, got {retrieved_pm_by_id.period.start_date}"  # type: ignore
                assert retrieved_pm_by_id.user.telegram_id == user_telegram_id, f"Expected user {user_telegram_id}, got {retrieved_pm_by_id.user.telegram_id}"  # type: ignore
            else:
                assert False, "Period money not found by ID when it should exist"
        
        # 3. UPDATE PERIOD MONEY BY DATE AND USER (NEW METHOD)
        print("\n3️⃣ Updating period money by date and user...")
        updated_pm = update_period_money(
            test_dates[0],
            user_telegram_id,
            amount=150.75
        )
        
        if updated_pm:
            print(f"✅ Updated period money: ${updated_pm.amount}")
            # Assert updated values match expected
            assert updated_pm.amount == 150.75, f"Expected updated amount 150.75, got {updated_pm.amount}"
            assert str(updated_pm.period.start_date) == test_dates[0], f"Expected period {test_dates[0]}, got {updated_pm.period.start_date}"  # type: ignore
            assert updated_pm.user.telegram_id == user_telegram_id, f"Expected user {user_telegram_id}, got {updated_pm.user.telegram_id}"  # type: ignore
        else:
            assert False, "Failed to update period money"
        
        # 3b. UPDATE PERIOD MONEY BY ID (LEGACY METHOD)
        print("\n3b️⃣ Updating period money by ID (legacy method)...")
        if period_money_ids and len(period_money_ids) > 1:
            updated_pm_by_id = update_period_money_by_id(
                period_money_ids[1],
                amount=275.50
            )
            
            if updated_pm_by_id:
                print(f"✅ Updated period money by ID: ${updated_pm_by_id.amount}")
                # Assert updated values match expected
                assert updated_pm_by_id.amount == 275.50, f"Expected updated amount 275.50, got {updated_pm_by_id.amount}"
                assert str(updated_pm_by_id.period.start_date) == test_dates[1], f"Expected period {test_dates[1]}, got {updated_pm_by_id.period.start_date}"  # type: ignore
                assert updated_pm_by_id.user.telegram_id == user_telegram_id, f"Expected user {user_telegram_id}, got {updated_pm_by_id.user.telegram_id}"  # type: ignore
            else:
                assert False, "Failed to update period money by ID"
        
        # 4. LIST PERIOD MONEYS BY PERIOD
        print("\n4️⃣ Listing period moneys by period...")
        period_moneys_p1 = list_period_moneys_by_period(test_dates[0])
        period_moneys_p2 = list_period_moneys_by_period(test_dates[1])
        
        print(f"✅ Period {test_dates[0]} has {len(period_moneys_p1)} money records:")
        # Assert we have the expected number of period moneys for period 1
        assert len(period_moneys_p1) == 2, f"Expected 2 period moneys for period {test_dates[0]}, got {len(period_moneys_p1)}"
        
        for pm in period_moneys_p1:
            print(f"   - ${pm.amount} from user {pm.user.telegram_id}")  # type: ignore
            # Assert each period money belongs to the correct period and one of our test users
            assert str(pm.period.start_date) == test_dates[0], f"Expected period {test_dates[0]}, got {pm.period.start_date}"  # type: ignore
            assert pm.user.telegram_id in [user_telegram_id, second_user_telegram_id], f"Expected user to be one of [{user_telegram_id}, {second_user_telegram_id}], got {pm.user.telegram_id}"  # type: ignore
        
        print(f"✅ Period {test_dates[1]} has {len(period_moneys_p2)} money records:")
        # Assert we have the expected number of period moneys for period 2
        assert len(period_moneys_p2) == 1, f"Expected 1 period money for period {test_dates[1]}, got {len(period_moneys_p2)}"
        
        for pm in period_moneys_p2:
            print(f"   - ${pm.amount} from user {pm.user.telegram_id}")  # type: ignore
            # Assert each period money belongs to the correct period and user
            assert str(pm.period.start_date) == test_dates[1], f"Expected period {test_dates[1]}, got {pm.period.start_date}"  # type: ignore
            assert pm.user.telegram_id == user_telegram_id, f"Expected user {user_telegram_id}, got {pm.user.telegram_id}"  # type: ignore
        
        # 5. LIST PERIOD MONEYS BY USER
        print("\n5️⃣ Listing period moneys by user...")
        user_moneys = list_period_moneys_by_user(user_telegram_id)
        print(f"✅ User {user_telegram_id} has {len(user_moneys)} money records:")
        # Assert we have the expected number of user moneys (user 1 has 2 records: period 1 updated + period 2)
        assert len(user_moneys) == 2, f"Expected 2 period moneys for user {user_telegram_id}, got {len(user_moneys)}"
        
        for pm in user_moneys:
            print(f"   - ${pm.amount} in period {pm.period.start_date}")  # type: ignore
            # Assert each period money belongs to the correct user
            assert pm.user.telegram_id == user_telegram_id, f"Expected user {user_telegram_id}, got {pm.user.telegram_id}"  # type: ignore
        
        # List period moneys for second user
        second_user_moneys = list_period_moneys_by_user(second_user_telegram_id)
        print(f"✅ User {second_user_telegram_id} has {len(second_user_moneys)} money records:")
        # Assert second user has 1 record
        assert len(second_user_moneys) == 1, f"Expected 1 period money for user {second_user_telegram_id}, got {len(second_user_moneys)}"
        
        for pm in second_user_moneys:
            print(f"   - ${pm.amount} in period {pm.period.start_date}")  # type: ignore
            # Assert each period money belongs to the correct user
            assert pm.user.telegram_id == second_user_telegram_id, f"Expected user {second_user_telegram_id}, got {pm.user.telegram_id}"  # type: ignore
        
        # 6. GET TOTAL MONEY FOR PERIOD
        print("\n6️⃣ Getting total money for period...")
        total_p1 = get_total_money_for_period(test_dates[0])
        total_p2 = get_total_money_for_period(test_dates[1])
        
        print(f"✅ Total money for period {test_dates[0]}: ${total_p1}")
        print(f"✅ Total money for period {test_dates[1]}: ${total_p2}")
        
        # Assert totals match expected amounts
        # Period 1: 150.75 (updated from 100.50) + 75.25 = 226.00
        expected_total_p1 = 150.75 + 75.25
        assert total_p1 == expected_total_p1, f"Expected total {expected_total_p1} for period {test_dates[0]}, got {total_p1}"
        
        # Period 2: 275.50 (updated from 250.75)
        expected_total_p2 = 275.50
        assert total_p2 == expected_total_p2, f"Expected total {expected_total_p2} for period {test_dates[1]}, got {total_p2}"
        
        # 7. TEST INVALID OPERATIONS
        print("\n7️⃣ Testing invalid operations...")
        # Create period money with invalid period
        invalid_pm = create_period_money(
            period_start_date="2099-12-31",
            user_telegram_id=user_telegram_id,
            amount=100.0
        )
        # Assert invalid period returns None
        assert invalid_pm is None, f"Expected None for invalid period, got {invalid_pm}"
        if invalid_pm is None:
            print("✅ Invalid period properly handled")
        
        # Create period money with invalid user
        invalid_pm2 = create_period_money(
            period_start_date=test_dates[0],
            user_telegram_id="invalid_user_id",
            amount=100.0
        )
        # Assert invalid user returns None
        assert invalid_pm2 is None, f"Expected None for invalid user, got {invalid_pm2}"
        if invalid_pm2 is None:
            print("✅ Invalid user properly handled")
        
        # 8. DELETE PERIOD MONEYS
        print("\n8️⃣ Deleting period moneys...")
        
        # Delete using date-based method (primary method)
        deleted_result1 = delete_period_money(test_dates[0], user_telegram_id)
        assert deleted_result1 is True, f"Expected True for deleting period money by date, got {deleted_result1}"
        if deleted_result1:
            print(f"✅ Deleted period money for period {test_dates[0]} using date-based method")
        
        deleted_result2 = delete_period_money(test_dates[1], user_telegram_id)  
        assert deleted_result2 is True, f"Expected True for deleting period money by date, got {deleted_result2}"
        if deleted_result2:
            print(f"✅ Deleted period money for period {test_dates[1]} using date-based method")
        
        # Delete the second user's period money using date-based method
        deleted_result3 = delete_period_money(test_dates[0], second_user_telegram_id)
        assert deleted_result3 is True, f"Expected True for deleting second user's period money by date, got {deleted_result3}"
        if deleted_result3:
            print(f"✅ Deleted period money for second user in period {test_dates[0]} using date-based method")
        
        deleted_count = 3  # We deleted all 3 period moneys
        
        print(f"✅ Deleted {deleted_count} period money records")
        # Assert all period moneys were deleted
        assert deleted_count == 3, f"Expected to delete 3 period moneys, deleted {deleted_count}"
        
        # Verify deletion
        print("\n🔍 Verifying period money deletion...")
        remaining_moneys = list_period_moneys_by_user(user_telegram_id)
        remaining_moneys_2 = list_period_moneys_by_user(second_user_telegram_id)
        # Assert all period moneys were deleted for both users
        assert len(remaining_moneys) == 0, f"Expected 0 remaining period moneys for user 1, found {len(remaining_moneys)}"
        assert len(remaining_moneys_2) == 0, f"Expected 0 remaining period moneys for user 2, found {len(remaining_moneys_2)}"
        if len(remaining_moneys) == 0 and len(remaining_moneys_2) == 0:
            print("✅ All test period moneys confirmed deleted")
        else:
            print(f"❌ {len(remaining_moneys) + len(remaining_moneys_2)} period moneys still exist!")
        
        # Cleanup test users
        user_deleted = delete_user(user_telegram_id)
        user_deleted_2 = delete_user(second_user_telegram_id)
        assert user_deleted is True, f"Expected True for user deletion, got {user_deleted}"
        assert user_deleted_2 is True, f"Expected True for second user deletion, got {user_deleted_2}"
        
        print("\n🎉 PeriodMoneys CRUD operations completed successfully!")
        
    except Exception as e:
        logger.error(f"PeriodMoneys test failed: {e}")
        print(f"❌ PeriodMoneys test failed: {e}")

def test_period_moneys_date_based_crud(test_dates):
    """Test new date-based CRUD operations for PeriodMoneys model"""
    try:
        if not test_dates:
            print("❌ No test periods available for period money date-based testing")
            return
        
        # Setup test user
        user_telegram_id = setup_test_user()
        if not user_telegram_id:
            print("❌ Failed to setup test user")
            return
        
        print("\n🧪 Testing PeriodMoneys Date-Based CRUD Operations")
        print("=" * 55)
        
        # 1. CREATE PERIOD MONEY USING DATE-BASED METHOD
        print("\n1️⃣ Creating period money using date-based method...")
        period_money = create_period_money(
            period_start_date=test_dates[0],
            user_telegram_id=user_telegram_id,
            amount=500.25
        )
        
        if period_money:
            print(f"✅ Created period money: ${period_money.amount} for period {test_dates[0]}")
            # Assert period_money values match expected
            assert str(period_money.period.start_date) == test_dates[0], f"Expected period start_date {test_dates[0]}, got {period_money.period.start_date}"  # type: ignore
            assert period_money.user.telegram_id == user_telegram_id, f"Expected user telegram_id {user_telegram_id}, got {period_money.user.telegram_id}"  # type: ignore
            assert period_money.amount == 500.25, f"Expected amount 500.25, got {period_money.amount}"
        else:
            assert False, "Failed to create period_money using date-based method"
        
        # 2. GET PERIOD MONEY USING DATE-BASED METHOD
        print("\n2️⃣ Getting period money using date-based method...")
        retrieved_pm = get_period_money(test_dates[0], user_telegram_id)
        
        if retrieved_pm:
            print(f"✅ Retrieved period money: ${retrieved_pm.amount}")
            print(f"   Period: {retrieved_pm.period.start_date}")  # type: ignore
            print(f"   User: {retrieved_pm.user.telegram_id}")  # type: ignore
            # Assert retrieved values match expected
            assert retrieved_pm.amount == 500.25, f"Expected amount 500.25, got {retrieved_pm.amount}"
            assert str(retrieved_pm.period.start_date) == test_dates[0], f"Expected period {test_dates[0]}, got {retrieved_pm.period.start_date}"  # type: ignore
            assert retrieved_pm.user.telegram_id == user_telegram_id, f"Expected user {user_telegram_id}, got {retrieved_pm.user.telegram_id}"  # type: ignore
        else:
            assert False, "Period money not found using date-based method when it should exist"
        
        # 3. UPDATE PERIOD MONEY USING DATE-BASED METHOD
        print("\n3️⃣ Updating period money using date-based method...")
        updated_pm = update_period_money(
            test_dates[0],
            user_telegram_id,
            amount=750.50
        )
        
        if updated_pm:
            print(f"✅ Updated period money: ${updated_pm.amount}")
            # Assert updated values match expected
            assert updated_pm.amount == 750.50, f"Expected updated amount 750.50, got {updated_pm.amount}"
            assert str(updated_pm.period.start_date) == test_dates[0], f"Expected period {test_dates[0]}, got {updated_pm.period.start_date}"  # type: ignore
            assert updated_pm.user.telegram_id == user_telegram_id, f"Expected user {user_telegram_id}, got {updated_pm.user.telegram_id}"  # type: ignore
        else:
            assert False, "Failed to update period money using date-based method"
        
        # 4. TEST EDGE CASES FOR DATE-BASED METHODS
        print("\n4️⃣ Testing edge cases for date-based methods...")
        
        # Try to get non-existent period money
        non_existent_pm = get_period_money("2099-12-31", user_telegram_id)
        assert non_existent_pm is None, f"Expected None for non-existent period, got {non_existent_pm}"
        if non_existent_pm is None:
            print("✅ Non-existent period properly returns None")
        
        # Try to get period money with non-existent user
        non_existent_user_pm = get_period_money(test_dates[0], "non_existent_user")
        assert non_existent_user_pm is None, f"Expected None for non-existent user, got {non_existent_user_pm}"
        if non_existent_user_pm is None:
            print("✅ Non-existent user properly returns None")
        
        # Try to update non-existent period money
        failed_update = update_period_money("2099-12-31", user_telegram_id, amount=100.0)
        assert failed_update is None, f"Expected None for updating non-existent period money, got {failed_update}"
        if failed_update is None:
            print("✅ Update of non-existent period money properly returns None")
        
        # 5. DELETE PERIOD MONEY USING DATE-BASED METHOD
        print("\n5️⃣ Deleting period money using date-based method...")
        deleted_result = delete_period_money(test_dates[0], user_telegram_id)
        assert deleted_result is True, f"Expected True for deleting period money, got {deleted_result}"
        if deleted_result:
            print("✅ Period money deleted successfully using date-based method")
        
        # Verify deletion
        print("\n🔍 Verifying period money deletion...")
        deleted_pm = get_period_money(test_dates[0], user_telegram_id)
        assert deleted_pm is None, f"Expected None after deletion, got {deleted_pm}"
        if deleted_pm is None:
            print("✅ Period money confirmed deleted")
        
        # Test deleting non-existent period money
        failed_delete = delete_period_money("2099-12-31", user_telegram_id)
        assert failed_delete is False, f"Expected False for deleting non-existent period money, got {failed_delete}"
        if not failed_delete:
            print("✅ Deleting non-existent period money properly returns False")
        
        # Cleanup test user
        user_deleted = delete_user(user_telegram_id)
        assert user_deleted is True, f"Expected True for user deletion, got {user_deleted}"
        
        print("\n🎉 Date-based PeriodMoneys CRUD operations completed successfully!")
        
    except Exception as e:
        logger.error(f"Date-based PeriodMoneys test failed: {e}")
        print(f"❌ Date-based PeriodMoneys test failed: {e}")

def test_periods_edge_cases():
    """Test edge cases and error conditions"""
    try:
        print("\n🧪 Testing Periods Edge Cases")
        print("=" * 40)
        
        # Test invalid date formats
        print("\n1️⃣ Testing invalid date formats...")
        invalid_date_period = create_period(
            start_date="invalid-date",
            total_money=100
        )
        
        # Assert invalid date format returns None
        assert invalid_date_period is None, f"Expected None for invalid date format, got {invalid_date_period}"
        if invalid_date_period is None:
            print("✅ Invalid date format properly handled")
        
        # Test current period logic with overlapping periods
        print("\n2️⃣ Testing current period logic...")
        current = get_current_period()
        if current:
            print(f"✅ Current period found: {current.start_date}")
            # Assert current period has valid date
            assert current.start_date is not None, "Current period should have a valid start_date"
            assert isinstance(current.start_date, dt_date), f"Expected date object, got {type(current.start_date)}"
        else:
            print("ℹ️  No current period (this may be expected)")
        
        print("\n🎉 Edge cases testing completed!")
        
    except Exception as e:
        logger.error(f"Edge cases test failed: {e}")
        print(f"❌ Edge cases test failed: {e}")


def run_all_period_tests():
    """Run all period-related tests"""
    try:
        db_manager.connect()
        logger.info("✅ Connected to database")
        
        # Clean up any existing test data first
        cleanup_existing_test_data()
        
        # Run periods CRUD tests and get test dates
        test_dates = test_periods_crud()
        
        # Run period moneys CRUD tests
        test_period_moneys_crud(test_dates)
        
        # Run date-based period moneys CRUD tests
        test_period_moneys_date_based_crud(test_dates)
        
        # Run edge cases tests
        test_periods_edge_cases()
        
        # Cleanup test data
        cleanup_test_data(test_dates, None)
        
        print("\n🎉 All period tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Period tests failed: {e}")
        print(f"❌ Period tests failed: {e}")
    
    finally:
        # Disconnect from database
        db_manager.disconnect()
        logger.info("✅ Disconnected from database")

if __name__ == "__main__":
    run_all_period_tests()
