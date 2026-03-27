from datetime import date as dt_date
from mongoengine import DoesNotExist, ValidationError
from schemas.shuttlecock_batches import ShuttlecockBatches
from schemas.periods import Periods
from typing import Optional, List, cast
import logging

logger = logging.getLogger(__name__)


class ShuttlecockBatchService:

    @staticmethod
    def create_batch(
        period_start_date: str,
        purchase_date: str,
        total_price: float,
        tube_count: Optional[int] = None,
    ) -> Optional[ShuttlecockBatches]:
        try:
            period = cast(Periods, Periods.objects.get(start_date=dt_date.fromisoformat(period_start_date)))  # type: ignore
            batch = ShuttlecockBatches(
                purchase_date=dt_date.fromisoformat(purchase_date),
                total_price=total_price,
                tube_count=tube_count,
                period=period,
            )
            batch.save()
            logger.info(f"Created shuttlecock batch on {purchase_date} for period {period_start_date}")
            return batch
        except DoesNotExist:
            logger.error(f"Period with start_date {period_start_date} not found")
        except ValidationError as e:
            logger.error(f"Validation error creating shuttlecock batch: {e}")
        except Exception as e:
            logger.error(f"Failed to create shuttlecock batch: {e}")
        return None

    @staticmethod
    def get_batch_by_purchase_date(purchase_date: str) -> Optional[ShuttlecockBatches]:
        try:
            return cast(
                Optional[ShuttlecockBatches],
                ShuttlecockBatches.objects.get(purchase_date=dt_date.fromisoformat(purchase_date)),  # type: ignore
            )
        except DoesNotExist:
            logger.info(f"Shuttlecock batch on {purchase_date} not found")
        except Exception as e:
            logger.error(f"Error getting shuttlecock batch on {purchase_date}: {e}")
        return None

    @staticmethod
    def list_batches_by_period(period_start_date: str) -> List[ShuttlecockBatches]:
        try:
            period = cast(Periods, Periods.objects.get(start_date=dt_date.fromisoformat(period_start_date)))  # type: ignore
            return list(ShuttlecockBatches.objects.filter(period=period))  # type: ignore
        except DoesNotExist:
            logger.error(f"Period with start_date {period_start_date} not found")
        except Exception as e:
            logger.error(f"Failed to list shuttlecock batches for period {period_start_date}: {e}")
        return []

    @staticmethod
    def get_total_shuttlecock_cost_for_period(period_start_date: str) -> float:
        batches = ShuttlecockBatchService.list_batches_by_period(period_start_date)
        return sum(b.total_price for b in batches)  # type: ignore

    @staticmethod
    def delete_batch(purchase_date: str) -> bool:
        try:
            batch = cast(ShuttlecockBatches, ShuttlecockBatches.objects.get(purchase_date=dt_date.fromisoformat(purchase_date)))  # type: ignore
            batch.delete()
            logger.info(f"Deleted shuttlecock batch on {purchase_date}")
            return True
        except DoesNotExist:
            logger.error(f"Shuttlecock batch on {purchase_date} not found for deletion")
        except Exception as e:
            logger.error(f"Failed to delete shuttlecock batch on {purchase_date}: {e}")
        return False


def create_batch(
    period_start_date: str,
    purchase_date: str,
    total_price: float,
    tube_count: Optional[int] = None,
) -> Optional[ShuttlecockBatches]:
    return ShuttlecockBatchService.create_batch(period_start_date, purchase_date, total_price, tube_count)

def get_batch(purchase_date: str) -> Optional[ShuttlecockBatches]:
    return ShuttlecockBatchService.get_batch_by_purchase_date(purchase_date)

def list_batches_by_period(period_start_date: str) -> List[ShuttlecockBatches]:
    return ShuttlecockBatchService.list_batches_by_period(period_start_date)

def get_total_shuttlecock_cost_for_period(period_start_date: str) -> float:
    return ShuttlecockBatchService.get_total_shuttlecock_cost_for_period(period_start_date)

def delete_batch(purchase_date: str) -> bool:
    return ShuttlecockBatchService.delete_batch(purchase_date)
