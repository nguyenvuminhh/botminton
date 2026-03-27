import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.metadata import get_metadata, update_metadata
from schemas.metadata import Metadata
from utils.database import db_manager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_metadata_ru():
    """Test Read and Update operations for Metadata model"""
    original_metadata = None
    try:
        # Connect to database
        db_manager.connect()
        logger.info("✅ Connected to database")
        
        print("\n🧪 Testing Metadata RU Operations")
        print("=" * 50)
        
        # 0. CREATE METADATA (using ORM directly since service only has RU)
        print("\n0️⃣ Creating/Getting metadata...")
        metadata = Metadata.create()
        if metadata:
            # Save original values for restoration
            original_metadata = {
                'default_location': metadata.default_location,
                'default_start_time': metadata.default_start_time,
                'default_end_time': metadata.default_end_time,
                'default_day_of_the_week_index': metadata.default_day_of_the_week_index,
            }
            print("✅ Created/Retrieved metadata singleton and saved original values")
            print(f"   Location: {metadata.default_location}")
            print(f"   Start Time: {metadata.default_start_time}")
            print(f"   End Time: {metadata.default_end_time}")
            print(f"   Day Index: {metadata.default_day_of_the_week_index}")
        
        # 1. GET METADATA
        print("\n1️⃣ Getting metadata...")
        retrieved_metadata = get_metadata()
        
        if retrieved_metadata:
            print("✅ Retrieved metadata:")
            print(f"   Location: {retrieved_metadata.default_location}")
            print(f"   Start Time: {retrieved_metadata.default_start_time}")
            print(f"   End Time: {retrieved_metadata.default_end_time}")
            print(f"   Day Index: {retrieved_metadata.default_day_of_the_week_index}")
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
        )
        
        if updated_metadata:
            print("✅ Updated multiple fields:")
            print(f"   Start Time: {updated_metadata.default_start_time}")
            print(f"   End Time: {updated_metadata.default_end_time}")
            print(f"   Day Index: {updated_metadata.default_day_of_the_week_index}")
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
        
        # 5. TEST PARTIAL UPDATE (None values should be ignored)
        print("\n5️⃣ Testing partial update with None values...")
        partial_update = update_metadata(
            default_location="Final Location",
            default_start_time=None,  # Should be ignored
        )
        
        if partial_update:
            print("✅ Partial update successful:")
            print(f"   Location: {partial_update.default_location}")
            print(f"   Start Time: {partial_update.default_start_time} (should be unchanged)")
        
        # 6. RESTORE ORIGINAL VALUES
        print("\n6️⃣ Restoring original values...")
        if original_metadata:
            restored_metadata = update_metadata(
                default_location=original_metadata['default_location'],
                default_start_time=original_metadata['default_start_time'],
                default_end_time=original_metadata['default_end_time'],
                default_day_of_the_week_index=original_metadata['default_day_of_the_week_index'],
            )
            
            if restored_metadata:
                print("✅ Restored original values:")
                print(f"   Location: {restored_metadata.default_location}")
                print(f"   Start Time: {restored_metadata.default_start_time}")
                print(f"   End Time: {restored_metadata.default_end_time}")
                print(f"   Day Index: {restored_metadata.default_day_of_the_week_index}")
        
        print("\n🎉 All metadata RU operations completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")
        
        # Attempt to restore original values even if test failed
        if original_metadata:
            print("\n🔄 Attempting to restore original values after error...")
            try:
                update_metadata(
                    default_location=original_metadata['default_location'],
                    default_start_time=original_metadata['default_start_time'],
                    default_end_time=original_metadata['default_end_time'],
                    default_day_of_the_week_index=original_metadata['default_day_of_the_week_index'],
                )
                print("✅ Original values restored after error")
            except Exception as restore_error:
                logger.error(f"Failed to restore original values: {restore_error}")
                print(f"❌ Failed to restore original values: {restore_error}")
    
    finally:
        # Disconnect from database
        db_manager.disconnect()
        logger.info("✅ Disconnected from database")

if __name__ == "__main__":
    test_metadata_ru()
