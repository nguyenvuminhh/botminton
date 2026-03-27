import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas.period_moneys import PeriodMoneys
from schemas.periods import Periods
from schemas.sessions import Sessions
from schemas.session_participants import SessionParticipants
from schemas.shuttlecock_batches import ShuttlecockBatches
from schemas.users import Users
from schemas.venues import Venues
from tests.test_basic import test_basic_functionality
from tests.test_calculations import test_session_cost_calculation
from tests.test_users import test_users_crud
from tests.test_sessions import test_sessions_crud, test_session_edge_cases
from tests.test_periods import run_all_period_tests
from tests.test_session_participants import test_session_participants_crud, test_session_participants_edge_cases
from tests.test_period_moneys import test_period_money_payment_status
from tests.test_venues import test_venues_crud
from tests.test_shuttlecock_batches import test_shuttlecock_batches_crud
from utils.database import db_manager

def clear_database():
    """Clear the database before running tests"""
    db_manager.connect()

    Users.drop_collection()
    Periods.drop_collection()
    PeriodMoneys.drop_collection()
    Sessions.drop_collection()
    SessionParticipants.drop_collection()
    ShuttlecockBatches.drop_collection()
    Venues.drop_collection()
    print("✅ Database cleared")

def run_all_tests():
    """Run all available tests"""
    print("🚀 Running All Tests")
    print("=" * 50)
    
    # Test 2: Basic Functionality
    print("\n📋 Test 2: Basic Functionality")
    test_basic_functionality()
    
    # Test 3: Users CRUD
    print("\n📋 Test 3: Users CRUD Operations")
    test_users_crud()
    
    # Test 4: Sessions CRUD
    print("\n📋 Test 4: Sessions CRUD Operations")
    test_sessions_crud()
    
    # Test 5: Sessions Edge Cases
    print("\n📋 Test 5: Sessions Edge Cases")
    test_session_edge_cases()
    
    # Test 6: Periods & PeriodMoneys CRUD
    print("\n📋 Test 6: Periods & PeriodMoneys Operations")
    run_all_period_tests()

    # Test 7: Session Participants CRUD
    print("\n📋 Test 7: Session Participants CRUD Operations")
    test_session_participants_crud()

    # Test 8: Session Participants Edge Cases
    print("\n📋 Test 8: Session Participants Edge Cases")
    test_session_participants_edge_cases()

    # Test 9: Period Money Payment Status
    print("\n📋 Test 9: Period Money Payment Status")
    test_period_money_payment_status()

    # Test 10: Venues CRUD
    print("\n📋 Test 10: Venues CRUD")
    test_venues_crud()

    # Test 11: Shuttlecock Batches CRUD
    print("\n📋 Test 11: Shuttlecock Batches CRUD")
    test_shuttlecock_batches_crud()

    # Test 12: Calculation Service
    print("\n📋 Test 12: Calculation Service")
    test_session_cost_calculation()

    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    clear_database()
    run_all_tests()
    clear_database()
