import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_basic import test_basic_functionality
from tests.test_users import test_users_crud
from tests.test_sessions import test_sessions_crud, test_session_edge_cases
from tests.test_periods import run_all_period_tests
from tests.test_session_participants import test_session_participants_crud, test_session_participants_edge_cases

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

    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    run_all_tests()
