import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.shuttlecock_batches import (
    create_batch, get_batch, list_batches_by_period,
    get_total_shuttlecock_cost_for_period, delete_batch,
)
from services.periods import create_period, delete_period
from utils.database import db_manager
from datetime import date as dt_date
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PERIOD_START = "2020-01-01"
BATCH_DATE_1 = "2020-01-05"
BATCH_DATE_2 = "2020-01-12"


def test_shuttlecock_batches_crud():
    try:
        db_manager.connect()
        print("\n🧪 Testing ShuttlecockBatches CRUD")
        print("=" * 40)

        # Cleanup
        delete_batch(BATCH_DATE_1)
        delete_batch(BATCH_DATE_2)
        delete_period(PERIOD_START)

        # Setup period
        period = create_period(start_date=PERIOD_START)
        assert period is not None

        # CREATE
        batch1 = create_batch(
            period_start_date=PERIOD_START,
            purchase_date=BATCH_DATE_1,
            total_price=11.4,
            tube_count=12,
        )
        assert batch1 is not None
        assert batch1.total_price == 11.4
        assert batch1.tube_count == 12
        print(f"✅ Created batch: {batch1.purchase_date}, {batch1.total_price} €")

        batch2 = create_batch(
            period_start_date=PERIOD_START,
            purchase_date=BATCH_DATE_2,
            total_price=9.0,
        )
        assert batch2 is not None
        print(f"✅ Created batch: {batch2.purchase_date}, {batch2.total_price} €")

        # GET
        fetched = get_batch(BATCH_DATE_1)
        assert fetched is not None
        assert fetched.total_price == 11.4
        print("✅ Fetched batch by purchase_date")

        # LIST BY PERIOD
        batches = list_batches_by_period(PERIOD_START)
        assert len(batches) == 2
        print(f"✅ Listed {len(batches)} batches for period")

        # TOTAL COST
        total = get_total_shuttlecock_cost_for_period(PERIOD_START)
        assert abs(total - 20.4) < 0.001, f"Expected 20.4, got {total}"
        print(f"✅ Total shuttlecock cost: {total} €")

        # INVALID PERIOD
        bad = create_batch(period_start_date="2099-01-01", purchase_date="2099-01-10", total_price=5.0)
        assert bad is None
        print("✅ Invalid period handled")

        # DELETE
        assert delete_batch(BATCH_DATE_1) is True
        assert get_batch(BATCH_DATE_1) is None
        assert delete_batch(BATCH_DATE_2) is True
        print("✅ Deleted batches")

        delete_period(PERIOD_START)
        print("\n🎉 ShuttlecockBatches CRUD completed!")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")
        raise
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    test_shuttlecock_batches_crud()
