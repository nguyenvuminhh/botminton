from datetime import date as dt_date
import logging
from typing import List, Optional, cast

from bson import ObjectId
from mongoengine import DoesNotExist

from schemas.period_shuttlecock_uses import PeriodShuttlecockUses
from schemas.periods import Periods
from schemas.shuttlecock_batches import ShuttlecockBatches

logger = logging.getLogger(__name__)


class PeriodShuttlecockUseService:
    @staticmethod
    def create_use(
        period_start_date: str,
        batch_id: str,
        tubes_used: int,
    ) -> Optional[PeriodShuttlecockUses]:
        try:
            period = cast(
                Periods,
                Periods.objects.get(start_date=dt_date.fromisoformat(period_start_date)),  # type: ignore
            )
            batch = cast(ShuttlecockBatches, ShuttlecockBatches.objects.get(id=ObjectId(batch_id)))  # type: ignore
            use = PeriodShuttlecockUses(period=period, batch=batch, tubes_used=tubes_used)
            use.save()
            return use
        except DoesNotExist:
            logger.error(f"Period {period_start_date} or batch {batch_id} not found")
        except Exception as e:
            logger.error(f"Failed to create shuttlecock use: {e}")
        return None

    @staticmethod
    def list_uses_by_period(period_start_date: str) -> List[PeriodShuttlecockUses]:
        try:
            period = cast(
                Periods,
                Periods.objects.get(start_date=dt_date.fromisoformat(period_start_date)),  # type: ignore
            )
            return list(PeriodShuttlecockUses.objects.filter(period=period))  # type: ignore
        except DoesNotExist:
            logger.error(f"Period {period_start_date} not found")
        except Exception as e:
            logger.error(f"Failed to list shuttlecock uses for period {period_start_date}: {e}")
        return []

    @staticmethod
    def get_consumed_for_batch(batch_id: str) -> int:
        try:
            batch = cast(ShuttlecockBatches, ShuttlecockBatches.objects.get(id=ObjectId(batch_id)))  # type: ignore
            uses = PeriodShuttlecockUses.objects.filter(batch=batch)  # type: ignore
            return int(sum((u.tubes_used or 0) for u in uses))  # type: ignore
        except DoesNotExist:
            return 0
        except Exception as e:
            logger.error(f"Failed to get consumed count for batch {batch_id}: {e}")
            return 0

    @staticmethod
    def get_total_shuttlecock_cost_for_period(period_start_date: str) -> float:
        uses = PeriodShuttlecockUseService.list_uses_by_period(period_start_date)
        total = 0.0
        for u in uses:
            batch: ShuttlecockBatches = u.batch  # type: ignore
            if not batch or not batch.tube_count:  # type: ignore
                continue
            price_each = (batch.total_price or 0.0) / batch.tube_count  # type: ignore
            total += price_each * (u.tubes_used or 0)  # type: ignore
        return total

    @staticmethod
    def delete_use(use_id: str) -> bool:
        try:
            use = cast(PeriodShuttlecockUses, PeriodShuttlecockUses.objects.get(id=ObjectId(use_id)))  # type: ignore
            use.delete()
            return True
        except DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Failed to delete shuttlecock use {use_id}: {e}")
            return False


def create_use(period_start_date: str, batch_id: str, tubes_used: int) -> Optional[PeriodShuttlecockUses]:
    return PeriodShuttlecockUseService.create_use(period_start_date, batch_id, tubes_used)


def list_uses_by_period(period_start_date: str) -> List[PeriodShuttlecockUses]:
    return PeriodShuttlecockUseService.list_uses_by_period(period_start_date)


def get_consumed_for_batch(batch_id: str) -> int:
    return PeriodShuttlecockUseService.get_consumed_for_batch(batch_id)


def get_total_shuttlecock_cost_for_period(period_start_date: str) -> float:
    return PeriodShuttlecockUseService.get_total_shuttlecock_cost_for_period(period_start_date)


def delete_use(use_id: str) -> bool:
    return PeriodShuttlecockUseService.delete_use(use_id)
