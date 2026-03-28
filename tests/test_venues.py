import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.venues import create_venue, get_venue_by_name, update_venue, delete_venue, list_all_venues
from utils.database import db_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEST_NAME = "Test Unisport student"
TEST_LOCATION = "Unisport"
TEST_PRICE = 10.0


def test_venues_crud():
    try:
        db_manager.connect()
        print("\n🧪 Testing Venues CRUD")
        print("=" * 40)

        # Cleanup leftover
        delete_venue(TEST_NAME)

        # CREATE
        venue = create_venue(name=TEST_NAME, location=TEST_LOCATION, price_per_slot=TEST_PRICE)
        assert venue is not None, "Failed to create venue"
        assert venue.name == TEST_NAME
        assert venue.price_per_slot == TEST_PRICE
        print(f"✅ Created venue: {venue.name} @ {venue.price_per_slot} €/slot")

        # CREATE DUPLICATE returns existing
        duplicate = create_venue(name=TEST_NAME, location=TEST_LOCATION, price_per_slot=TEST_PRICE)
        assert duplicate is not None
        print("✅ Duplicate create returns existing")

        # GET
        fetched = get_venue_by_name(TEST_NAME)
        assert fetched is not None
        assert fetched.name == TEST_NAME
        print("✅ Fetched venue by name")

        # UPDATE
        updated = update_venue(TEST_NAME, price_per_slot=12.0)
        assert updated is not None
        assert updated.price_per_slot == 12.0
        print(f"✅ Updated price to {updated.price_per_slot}")

        # LIST
        venues = list_all_venues()
        names = [v.name for v in venues]
        assert TEST_NAME in names
        print(f"✅ Listed {len(venues)} venue(s)")

        # DELETE
        assert delete_venue(TEST_NAME) is True
        assert get_venue_by_name(TEST_NAME) is None
        print("✅ Deleted venue")

        # DELETE non-existent
        assert delete_venue("nonexistent") is False
        print("✅ Non-existent delete handled")

        print("\n🎉 Venues CRUD completed!")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")
        raise
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    test_venues_crud()
