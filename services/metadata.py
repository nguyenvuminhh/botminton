from orms.metadata import Metadata
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MetadataService:
    """Service class for metadata RU operations"""

    @staticmethod
    def get_metadata() -> Optional[Metadata]:
        try:
            metadata = Metadata.get()
            logger.debug("Retrieved metadata")
            return metadata

        except Exception as e:
            logger.error(f"Error getting metadata: {e}")
            return None

    
    @staticmethod
    def update_metadata(
        default_location: Optional[str] = None, 
        default_start_time: Optional[str] = None, 
        default_end_time: Optional[str] = None, 
        default_day_of_the_week_index: Optional[int] = None, 
        common_group_chat_id: Optional[str] = None, 
        admin_group_chat_id: Optional[str] = None
    ) -> Optional[Metadata]:
        try:
            metadata = Metadata.get()
        except Exception as e:
            logger.error(f"Error getting metadata for update: {e}")
            return None

        update_fields = {
            "default_location": default_location,
            "default_start_time": default_start_time,
            "default_end_time": default_end_time,
            "default_day_of_the_week_index": default_day_of_the_week_index,
            "common_group_chat_id": common_group_chat_id,
            "admin_group_chat_id": admin_group_chat_id,
        }

        for field, value in update_fields.items():
            if value is not None:
                setattr(metadata, field, value)

        metadata.save()
        logger.info("Updated metadata")
        return metadata
    

# ------------------------
# ✅ Convenience functions
# ------------------------
def get_metadata() -> Optional[Metadata]:
    return MetadataService.get_metadata()

def update_metadata(
    default_location: Optional[str] = None, 
    default_start_time: Optional[str] = None, 
    default_end_time: Optional[str] = None, 
    default_day_of_the_week_index: Optional[int] = None, 
    common_group_chat_id: Optional[str] = None, 
    admin_group_chat_id: Optional[str] = None
) -> Optional[Metadata]:
    return MetadataService.update_metadata(
        default_location=default_location,
        default_start_time=default_start_time,
        default_end_time=default_end_time,
        default_day_of_the_week_index=default_day_of_the_week_index,
        common_group_chat_id=common_group_chat_id,
        admin_group_chat_id=admin_group_chat_id
    )
