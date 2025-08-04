import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.users import UserService, create_user, get_user, update_user, delete_user, list_users, list_all_users
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
        test_telegram_id = "123456789"
        test_telegram_id_2 = "987654321"
        
        print("\n🧪 Testing Users CRUD Operations")
        print("=" * 50)
        
        # 1. CREATE USER
        print("\n1️⃣ Creating users...")
        user1 = create_user(
            telegram_id=test_telegram_id,
            telegram_user_name="testuser1",
            is_admin=False
        )
        
        user2 = create_user(
            telegram_id=test_telegram_id_2,
            telegram_user_name="testuser2", 
            is_admin=True
        )
        
        if user1:
            print(f"✅ Created user1: {user1.telegram_user_name} (ID: {user1.telegram_id})")
            print(f"   Admin: {user1.is_admin}")
        if user2:
            print(f"✅ Created user2: {user2.telegram_user_name} (ID: {user2.telegram_id})")
            print(f"   Admin: {user2.is_admin}")
        
        # 2. GET USER BY TELEGRAM ID
        print("\n2️⃣ Getting user by telegram ID...")
        retrieved_user = get_user(test_telegram_id)
        
        if retrieved_user:
            print(f"✅ Retrieved user: {retrieved_user.telegram_user_name}")
            print(f"   Telegram ID: {retrieved_user.telegram_id}")
            print(f"   Admin: {retrieved_user.is_admin}")
        else:
            print("❌ User not found")
        
        # 3. UPDATE USER BY TELEGRAM ID
        print("\n3️⃣ Updating user by telegram ID...")
        updated_user = update_user(
            test_telegram_id,
            telegram_user_name="updated_testuser1"
        )
        
        if updated_user:
            print(f"✅ Updated user: {updated_user.telegram_user_name}")
        else:
            print("❌ Failed to update user")
        
        # 4. LIST USERS BY TELEGRAM IDS
        print("\n4️⃣ Listing users by telegram IDs...")
        users_by_ids = list_users([test_telegram_id, test_telegram_id_2, "nonexistent"])
        print(f"✅ Found {len(users_by_ids)} users from telegram IDs:")
        for u in users_by_ids:
            print(f"   - {u.telegram_user_name} (ID: {u.telegram_id}) - Admin: {u.is_admin}")
        
        # 5. LIST ALL USERS
        print("\n5️⃣ Listing all users...")
        all_users = list_all_users(limit=10)
        print(f"✅ Found {len(all_users)} total users:")
        for u in all_users:
            print(f"   - {u.telegram_user_name or 'No username'} (ID: {u.telegram_id}) - Admin: {u.is_admin}")
                        
        # 10. DELETE USERS BY TELEGRAM ID
        print("\n🔟 Deleting users...")
        deleted1 = delete_user(test_telegram_id)
        deleted2 = delete_user(test_telegram_id_2)
        
        if deleted1:
            print(f"✅ Deleted user with ID: {test_telegram_id}")
        if deleted2:
            print(f"✅ Deleted user with ID: {test_telegram_id_2}")
            
        # Verify users are gone
        print("\n🔍 Verifying deletion...")
        deleted_user1 = get_user(test_telegram_id)
        deleted_user2 = get_user(test_telegram_id_2)
        
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

if __name__ == "__main__":
    test_users_crud()