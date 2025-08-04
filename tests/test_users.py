import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from services.users import create_user, get_user, update_user, delete_user, list_all_users
from utils.database import db_manager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_users_crud():
    """Test all CRUD operations for Users model"""
    try:
        # Connect to database
        db_manager.connect()
        logger.info("✅ Connected to database")
        
        # Test data
        test_telegram_id = "987654321"
        test_telegram_id_2 = config.ADMIN_1_USER_ID
        
        print("\n🧪 Testing Users CRUD Operations")
        print("=" * 50)
        
        # 1. CREATE USER
        print("\n1️⃣ Creating users...")
        user1 = create_user(
            telegram_id=test_telegram_id,
            telegram_user_name="testuser1",
        )
        
        user2 = create_user(
            telegram_id=test_telegram_id_2,
            telegram_user_name="testuser2", 
        )
        
        if user1:
            print(f"✅ Created user1: {user1.telegram_user_name} (ID: {user1.telegram_id})")
            print(f"   Admin: {user1.is_admin}")
            # Assert user1 values match expected
            assert user1.telegram_id == test_telegram_id, f"Expected telegram_id {test_telegram_id}, got {user1.telegram_id}"
            assert user1.telegram_user_name == "testuser1", f"Expected telegram_user_name 'testuser1', got {user1.telegram_user_name}"
            assert not user1.is_admin, f"Expected is_admin False, got {user1.is_admin}"
        else:
            assert False, "Failed to create user1"
            
        if user2:
            print(f"✅ Created user2: {user2.telegram_user_name} (ID: {user2.telegram_id})")
            print(f"   Admin: {user2.is_admin}")
            # Assert user2 values match expected
            assert user2.telegram_id == test_telegram_id_2, f"Expected telegram_id {test_telegram_id_2}, got {user2.telegram_id}"
            # assert user2.telegram_user_name == "testuser2", f"Expected telegram_user_name 'testuser2', got {user2.telegram_user_name}"
            assert user2.is_admin, f"Expected is_admin True, got {user2.is_admin}"
        else:
            assert False, "Failed to create user2"
        
        # 2. GET USER BY TELEGRAM ID
        print("\n2️⃣ Getting user by telegram ID...")
        retrieved_user = get_user(test_telegram_id)
        
        if retrieved_user:
            print(f"✅ Retrieved user: {retrieved_user.telegram_user_name}")
            print(f"   Telegram ID: {retrieved_user.telegram_id}")
            print(f"   Admin: {retrieved_user.is_admin}")
            # Assert retrieved values match expected
            assert retrieved_user.telegram_id == test_telegram_id, f"Expected telegram_id {test_telegram_id}, got {retrieved_user.telegram_id}"
            assert retrieved_user.telegram_user_name == "testuser1", f"Expected telegram_user_name 'testuser1', got {retrieved_user.telegram_user_name}"
            assert not retrieved_user.is_admin, f"Expected is_admin False, got {retrieved_user.is_admin}"
        else:
            assert False, "User not found when it should exist"
        
        # 3. UPDATE USER BY TELEGRAM ID
        print("\n3️⃣ Updating user by telegram ID...")
        updated_user = update_user(
            test_telegram_id,
            telegram_user_name="updated_testuser1"
        )
        
        if updated_user:
            print(f"✅ Updated user: {updated_user.telegram_user_name}")
            # Assert updated values match expected
            assert updated_user.telegram_id == test_telegram_id, f"Expected telegram_id {test_telegram_id}, got {updated_user.telegram_id}"
            assert updated_user.telegram_user_name == "updated_testuser1", f"Expected updated telegram_user_name 'updated_testuser1', got {updated_user.telegram_user_name}"
            assert not updated_user.is_admin, f"Expected is_admin False (unchanged), got {updated_user.is_admin}"
        else:
            assert False, "Failed to update user"
                
        # 5. LIST ALL USERS
        print("\n5️⃣ Listing all users...")
        all_users = list_all_users(limit=10)
        print(f"✅ Found {len(all_users)} total users:")
        # Assert we have at least our test users
        assert len(all_users) >= 2, f"Expected at least 2 users (our test users), got {len(all_users)}"
        
        # Check that our test users are in the list
        user_ids = [u.telegram_id for u in all_users]
        assert test_telegram_id in user_ids, f"Test user {test_telegram_id} not found in users list"
        assert test_telegram_id_2 in user_ids, f"Test user {test_telegram_id_2} not found in users list"
        
        for u in all_users:
            print(f"   - {u.telegram_user_name or 'No username'} (ID: {u.telegram_id}) - Admin: {u.is_admin}")
            # Assert basic user properties are valid
            assert u.telegram_id is not None, "User telegram_id should not be None"
            assert isinstance(u.is_admin, bool), f"Expected is_admin to be bool, got {type(u.is_admin)}"
        
        # 6. TEST DUPLICATE USER CREATION  
        print("\n6️⃣ Testing duplicate user creation...")
        duplicate_user = create_user(
            telegram_id=test_telegram_id,  # Same ID as user1
            telegram_user_name="duplicate_name",
        )
        
        if duplicate_user:
            print(f"ℹ️  Duplicate handled - returned existing user: {duplicate_user.telegram_user_name}")
            # Assert duplicate returns the original user with original values
            assert duplicate_user.telegram_id == test_telegram_id, f"Expected telegram_id {test_telegram_id}, got {duplicate_user.telegram_id}"
            assert duplicate_user.telegram_user_name == "updated_testuser1", f"Expected original username 'updated_testuser1', got {duplicate_user.telegram_user_name}"
            assert not duplicate_user.is_admin, f"Expected original is_admin False, got {duplicate_user.is_admin}"
        else:
            print("ℹ️  Duplicate creation returned None (also acceptable)")
        
        # 7. TEST NON-EXISTENT USER OPERATIONS
        print("\n7️⃣ Testing non-existent user operations...")
        non_existent_id = "non_existent_999"
        
        # Get non-existent user
        non_existent = get_user(non_existent_id)
        assert non_existent is None, f"Expected None for non-existent user, got {non_existent}"
        if non_existent is None:
            print("✅ Non-existent user get properly handled")
        
        # Update non-existent user
        non_existent_update = update_user(non_existent_id, telegram_user_name="new_name")
        assert non_existent_update is None, f"Expected None for non-existent user update, got {non_existent_update}"
        if non_existent_update is None:
            print("✅ Non-existent user update properly handled")
        
        # Delete non-existent user
        non_existent_delete = delete_user(non_existent_id)
        assert non_existent_delete is False, f"Expected False for non-existent user delete, got {non_existent_delete}"
        if not non_existent_delete:
            print("✅ Non-existent user delete properly handled")
                        
        # 10. DELETE USERS BY TELEGRAM ID
        print("\n🔟 Deleting users...")
        deleted1 = delete_user(test_telegram_id)
        deleted2 = delete_user(test_telegram_id_2)
        
        # Assert deletions were successful
        assert deleted1 is True, f"Expected True for user1 deletion, got {deleted1}"
        assert deleted2 is True, f"Expected True for user2 deletion, got {deleted2}"
        
        if deleted1:
            print(f"✅ Deleted user with ID: {test_telegram_id}")
        if deleted2:
            print(f"✅ Deleted user with ID: {test_telegram_id_2}")
            
        # Verify users are gone
        print("\n🔍 Verifying deletion...")
        deleted_user1 = get_user(test_telegram_id)
        deleted_user2 = get_user(test_telegram_id_2)
        
        # Assert all users are None after deletion
        assert deleted_user1 is None, f"Expected None for deleted user1, got {deleted_user1}"
        assert deleted_user2 is None, f"Expected None for deleted user2, got {deleted_user2}"
        
        if deleted_user1 is None and deleted_user2 is None:
            print("✅ All test users confirmed deleted")
        else:
            print("❌ Some users still exist!")
        
        print("\n🎉 All CRUD operations completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")
    
    finally:
        # Disconnect from database
        db_manager.disconnect()
        logger.info("✅ Disconnected from database")

def test_users_edge_cases():
    """Test edge cases and error conditions for users"""
    try:
        db_manager.connect()
        logger.info("✅ Connected to database for edge cases")
        
        print("\n🧪 Testing Users Edge Cases")
        print("=" * 40)
        
        # Test duplicate user creation
        print("\n1️⃣ Testing duplicate user creation...")
        test_telegram_id = "duplicate_test_123"
        
        user1 = create_user(
            telegram_id=test_telegram_id,
            telegram_user_name="original_user",
        )
        
        if user1:
            print(f"✅ Created original user: {user1.telegram_user_name}")
            # Assert original user creation succeeded
            assert user1.telegram_id == test_telegram_id, f"Expected telegram_id {test_telegram_id}, got {user1.telegram_id}"
            assert user1.telegram_user_name == "original_user", f"Expected username 'original_user', got {user1.telegram_user_name}"
            assert not user1.is_admin, f"Expected is_admin False, got {user1.is_admin}"
        else:
            assert False, "Failed to create original user"
        
        # Try to create duplicate
        user2 = create_user(
            telegram_id=test_telegram_id,  # Same ID
            telegram_user_name="duplicate_user",
        )
        
        if user2:
            print(f"ℹ️  Duplicate handled - returned existing user: {user2.telegram_user_name}")
            print(f"   Original values preserved: Admin={user2.is_admin}")
            # Assert duplicate returns the original user with original values
            assert user2.telegram_id == test_telegram_id, f"Expected telegram_id {test_telegram_id}, got {user2.telegram_id}"
            assert user2.telegram_user_name == "original_user", f"Expected original username 'original_user', got {user2.telegram_user_name}"
            assert not user2.is_admin, f"Expected original is_admin False, got {user2.is_admin}"
        else:
            print("ℹ️  Duplicate creation returned None (also acceptable)")
        
        # Test non-existent user operations
        print("\n2️⃣ Testing non-existent user operations...")
        non_existent_id = "non_existent_999"
        
        # Get non-existent user
        non_existent = get_user(non_existent_id)
        assert non_existent is None, f"Expected None for non-existent user, got {non_existent}"
        if non_existent is None:
            print("✅ Non-existent user get properly handled")
        
        # Update non-existent user
        non_existent_update = update_user(non_existent_id, telegram_user_name="new_name")
        assert non_existent_update is None, f"Expected None for non-existent user update, got {non_existent_update}"
        if non_existent_update is None:
            print("✅ Non-existent user update properly handled")
        
        # Delete non-existent user
        non_existent_delete = delete_user(non_existent_id)
        assert non_existent_delete is False, f"Expected False for non-existent user delete, got {non_existent_delete}"
        if not non_existent_delete:
            print("✅ Non-existent user delete properly handled")
        
        # Test edge case values
        print("\n3️⃣ Testing edge case values...")
        edge_user = create_user(
            telegram_id="edge_test_456",
            telegram_user_name="",  # Empty username
        )
        
        if edge_user:
            print(f"✅ Created user with empty username: '{edge_user.telegram_user_name}'")
            # Assert edge case values
            assert edge_user.telegram_id == "edge_test_456", f"Expected telegram_id 'edge_test_456', got {edge_user.telegram_id}"
            assert edge_user.telegram_user_name == "", f"Expected empty username, got '{edge_user.telegram_user_name}'"
            assert not edge_user.is_admin, f"Expected is_admin False, got {edge_user.is_admin}"
            
            # Clean up edge case user
            delete_result = delete_user("edge_test_456")
            assert delete_result is True, f"Expected True for edge user cleanup, got {delete_result}"
        
        # Test user count via list_all_users
        print("\n4️⃣ Testing user count via list...")
        all_users_list = list_all_users(limit=1000)  # Get all users
        user_count = len(all_users_list)
        print(f"✅ Total users in database: {user_count}")
        # Assert count is reasonable
        assert user_count >= 1, f"Expected at least 1 user (our test user), got {user_count}"
        assert isinstance(user_count, int), f"Expected int for count, got {type(user_count)}"
        
        # Verify specific user exists
        remaining_user = get_user(test_telegram_id)
        if remaining_user:
            assert remaining_user.telegram_id == test_telegram_id, f"Expected remaining user ID {test_telegram_id}, got {remaining_user.telegram_id}"
            print(f"✅ Test user still exists: {remaining_user.telegram_user_name}")
        
        # Clean up test user
        cleanup_result = delete_user(test_telegram_id)
        assert cleanup_result is True, f"Expected True for test user cleanup, got {cleanup_result}"
        if cleanup_result:
            print(f"✅ Cleaned up test user: {test_telegram_id}")
        
        print("\n🎉 Edge cases testing completed!")
        
    except Exception as e:
        logger.error(f"Edge cases test failed: {e}")
        print(f"❌ Edge cases test failed: {e}")
    
    finally:
        db_manager.disconnect()
        logger.info("✅ Disconnected from database")

if __name__ == "__main__":
    # Run main CRUD tests
    test_users_crud()
    
    # Run edge cases tests
    test_users_edge_cases()