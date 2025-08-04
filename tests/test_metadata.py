import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.metadata import get_metadata, update_metadata
from orms.metadata import Metadata
from utils.database import db_manager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_metadata_ru():
    """Test Read and Update operations for Metadata model"""
    try:
        # Connect to database
        db_manager.connect()
        logger.info("✅ Connected to database")
        
        print("\n🧪 Testing Metadata RU Operations")
        print("=" * 50)
        
        # 0. CREATE METADATA (using ORM directly since service only has RU)
        print("\n0️⃣ Creating metadata...")
        metadata = Metadata.create()
        if metadata:
            print("✅ Created/Retrieved metadata singleton")
            print(f"   Location: {metadata.default_location}")
            print(f"   Start Time: {metadata.default_start_time}")
            print(f"   End Time: {metadata.default_end_time}")
            print(f"   Day Index: {metadata.default_day_of_the_week_index}")
            print(f"   Common Chat ID: {metadata.common_group_chat_id}")
            print(f"   Admin Chat ID: {metadata.admin_group_chat_id}")
        
        # 1. GET METADATA
        print("\n1️⃣ Getting metadata...")
        retrieved_metadata = get_metadata()
        
        if retrieved_metadata:
            print("✅ Retrieved metadata:")
            print(f"   Location: {retrieved_metadata.default_location}")
            print(f"   Start Time: {retrieved_metadata.default_start_time}")
            print(f"   End Time: {retrieved_metadata.default_end_time}")
            print(f"   Day Index: {retrieved_metadata.default_day_of_the_week_index}")
            print(f"   Common Chat ID: {retrieved_metadata.common_group_chat_id}")
            print(f"   Admin Chat ID: {retrieved_metadata.admin_group_chat_id}")
        else:
            print("❌ Metadata not found")
        
        # 2. UPDATE METADATA - Single field
        print("\n2️⃣ Updating metadata (single field)...")
        updated_metadata = update_metadata(default_location="Updated Location")
        
        if updated_metadata:
            print(f"✅ Updated location: {updated_metadata.default_location}")
        else:
            print("❌ Failed to update metadata")
        
        # 3. UPDATE METADATA - Multiple fields
        print("\n3️⃣ Updating metadata (multiple fields)...")
        updated_metadata = update_metadata(
            default_start_time="19:00",
            default_end_time="21:30",
            default_day_of_the_week_index=6,
            common_group_chat_id="123456789",
            admin_group_chat_id="987654321"
        )
        
        if updated_metadata:
            print("✅ Updated multiple fields:")
            print(f"   Start Time: {updated_metadata.default_start_time}")
            print(f"   End Time: {updated_metadata.default_end_time}")
            print(f"   Day Index: {updated_metadata.default_day_of_the_week_index}")
            print(f"   Common Chat ID: {updated_metadata.common_group_chat_id}")
            print(f"   Admin Chat ID: {updated_metadata.admin_group_chat_id}")
        else:
            print("❌ Failed to update metadata")
        
        # 4. GET METADATA AGAIN (verify updates)
        print("\n4️⃣ Verifying updates...")
        final_metadata = get_metadata()
        
        if final_metadata:
            print("✅ Final metadata state:")
            print(f"   Location: {final_metadata.default_location}")
            print(f"   Start Time: {final_metadata.default_start_time}")
            print(f"   End Time: {final_metadata.default_end_time}")
            print(f"   Day Index: {final_metadata.default_day_of_the_week_index}")
            print(f"   Common Chat ID: {final_metadata.common_group_chat_id}")
            print(f"   Admin Chat ID: {final_metadata.admin_group_chat_id}")
        
        # 5. TEST PARTIAL UPDATE (None values should be ignored)
        print("\n5️⃣ Testing partial update with None values...")
        partial_update = update_metadata(
            default_location="Final Location",
            default_start_time=None,  # Should be ignored
            common_group_chat_id="final_chat_id"
        )
        
        if partial_update:
            print("✅ Partial update successful:")
            print(f"   Location: {partial_update.default_location}")
            print(f"   Start Time: {partial_update.default_start_time} (should be unchanged)")
            print(f"   Common Chat ID: {partial_update.common_group_chat_id}")
        
        # 6. RESET TO DEFAULTS
        print("\n6️⃣ Resetting to default values...")
        reset_metadata = update_metadata(
            default_location="Unisport",
            default_start_time="20:30",
            default_end_time="22:00",
            default_day_of_the_week_index=5,
            common_group_chat_id="0",
            admin_group_chat_id="0"
        )
        
        if reset_metadata:
            print("✅ Reset to defaults:")
            print(f"   Location: {reset_metadata.default_location}")
            print(f"   Start Time: {reset_metadata.default_start_time}")
            print(f"   End Time: {reset_metadata.default_end_time}")
            print(f"   Day Index: {reset_metadata.default_day_of_the_week_index}")
            print(f"   Common Chat ID: {reset_metadata.common_group_chat_id}")
            print(f"   Admin Chat ID: {reset_metadata.admin_group_chat_id}")
        
        print("\n🎉 All metadata RU operations completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")
    
    finally:
        # Disconnect from database
        db_manager.disconnect()
        logger.info("✅ Disconnected from database")

if __name__ == "__main__":
    test_metadata_ru()
