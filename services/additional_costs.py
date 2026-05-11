from datetime import date as dt_date
import logging
from typing import List, Optional, Sequence, cast

from bson import ObjectId
from mongoengine import DoesNotExist, NotUniqueError, ValidationError

from schemas.additional_cost_participants import AdditionalCostParticipants
from schemas.additional_costs import AdditionalCosts
from schemas.periods import Periods
from schemas.users import Users

logger = logging.getLogger(__name__)


class AdditionalCostService:
    @staticmethod
    def create_additional_cost(period_start_date: str, name: str, total_amount: float) -> Optional[AdditionalCosts]:
        try:
            if not name.strip():
                logger.error("Additional cost name is required")
                return None
            if total_amount < 0:
                logger.error("Additional cost total_amount must be non-negative")
                return None

            period = cast(Periods, Periods.objects.get(start_date=dt_date.fromisoformat(period_start_date)))  # type: ignore
            cost = AdditionalCosts(period=period, name=name.strip(), total_amount=total_amount)
            cost.save()
            logger.info("Created additional cost '%s' for period %s", name, period_start_date)
            return cost
        except DoesNotExist:
            logger.error("Period %s not found", period_start_date)
        except ValidationError as e:
            logger.error("Validation error creating additional cost: %s", e)
        except Exception as e:
            logger.error("Failed to create additional cost: %s", e)
        return None

    @staticmethod
    def get_additional_cost(cost_id: str) -> Optional[AdditionalCosts]:
        try:
            return cast(AdditionalCosts, AdditionalCosts.objects.get(id=ObjectId(cost_id)))  # type: ignore
        except DoesNotExist:
            return None
        except Exception as e:
            logger.error("Failed to get additional cost %s: %s", cost_id, e)
            return None

    @staticmethod
    def update_additional_cost(cost_id: str, **kwargs) -> Optional[AdditionalCosts]:
        try:
            cost = cast(AdditionalCosts, AdditionalCosts.objects.get(id=ObjectId(cost_id)))  # type: ignore
            if "name" in kwargs:
                name = str(kwargs["name"]).strip()
                if not name:
                    logger.error("Additional cost name is required")
                    return None
                cost.name = name  # type: ignore
            if "total_amount" in kwargs:
                total_amount = float(kwargs["total_amount"])
                if total_amount < 0:
                    logger.error("Additional cost total_amount must be non-negative")
                    return None
                cost.total_amount = total_amount  # type: ignore
            cost.save()
            return cost
        except DoesNotExist:
            return None
        except Exception as e:
            logger.error("Failed to update additional cost %s: %s", cost_id, e)
            return None

    @staticmethod
    def delete_additional_cost(cost_id: str) -> bool:
        try:
            cost = cast(AdditionalCosts, AdditionalCosts.objects.get(id=ObjectId(cost_id)))  # type: ignore
            cost.delete()
            return True
        except DoesNotExist:
            return False
        except Exception as e:
            logger.error("Failed to delete additional cost %s: %s", cost_id, e)
            return False

    @staticmethod
    def list_additional_costs_by_period(period_start_date: str) -> List[AdditionalCosts]:
        try:
            period = cast(Periods, Periods.objects.get(start_date=dt_date.fromisoformat(period_start_date)))  # type: ignore
            return list(AdditionalCosts.objects.filter(period=period).select_related())  # type: ignore
        except DoesNotExist:
            logger.error("Period %s not found", period_start_date)
        except Exception as e:
            logger.error("Failed to list additional costs for period %s: %s", period_start_date, e)
        return []

    @staticmethod
    def add_additional_cost_participant(
        cost_id: str,
        user_telegram_id: str,
        weight: float,
    ) -> Optional[AdditionalCostParticipants]:
        try:
            if weight <= 0:
                logger.error("Additional cost participant weight must be positive")
                return None

            cost = cast(AdditionalCosts, AdditionalCosts.objects.get(id=ObjectId(cost_id)))  # type: ignore
            user = cast(Users, Users.objects.get(telegram_id=user_telegram_id))  # type: ignore
            existing = AdditionalCostParticipants.objects(additional_cost=cost, user=user).first()  # type: ignore
            if existing:
                existing.weight = weight  # type: ignore
                existing.save()
                return cast(AdditionalCostParticipants, existing)

            participant = AdditionalCostParticipants(additional_cost=cost, user=user, weight=weight)
            participant.save()
            return participant
        except DoesNotExist:
            logger.error("Additional cost %s or user %s not found", cost_id, user_telegram_id)
        except NotUniqueError:
            return AdditionalCostService.add_additional_cost_participant(cost_id, user_telegram_id, weight)
        except ValidationError as e:
            logger.error("Validation error adding additional cost participant: %s", e)
        except Exception as e:
            logger.error("Failed to add additional cost participant: %s", e)
        return None

    @staticmethod
    def list_additional_cost_participants(cost_id: str) -> List[AdditionalCostParticipants]:
        try:
            cost = cast(AdditionalCosts, AdditionalCosts.objects.get(id=ObjectId(cost_id)))  # type: ignore
            return list(AdditionalCostParticipants.objects.filter(additional_cost=cost).select_related())  # type: ignore
        except DoesNotExist:
            logger.error("Additional cost %s not found", cost_id)
        except Exception as e:
            logger.error("Failed to list participants for additional cost %s: %s", cost_id, e)
        return []

    @staticmethod
    def list_participants_by_costs(costs: Sequence[AdditionalCosts]) -> List[AdditionalCostParticipants]:
        try:
            costs_list = list(costs)
            if not costs_list:
                return []
            return list(
                AdditionalCostParticipants.objects.filter(additional_cost__in=costs_list).select_related()  # type: ignore
            )
        except Exception as e:
            logger.error("Failed to list participants for additional costs: %s", e)
            return []

    @staticmethod
    def delete_additional_cost_participant(participant_id: str) -> bool:
        try:
            participant = cast(
                AdditionalCostParticipants,
                AdditionalCostParticipants.objects.get(id=ObjectId(participant_id)),  # type: ignore
            )
            participant.delete()
            return True
        except DoesNotExist:
            return False
        except Exception as e:
            logger.error("Failed to delete additional cost participant %s: %s", participant_id, e)
            return False

    @staticmethod
    def remove_additional_cost_participant(cost_id: str, user_telegram_id: str) -> bool:
        try:
            cost = cast(AdditionalCosts, AdditionalCosts.objects.get(id=ObjectId(cost_id)))  # type: ignore
            user = cast(Users, Users.objects.get(telegram_id=user_telegram_id))  # type: ignore
            participant = AdditionalCostParticipants.objects.get(additional_cost=cost, user=user)  # type: ignore
            participant.delete()
            return True
        except DoesNotExist:
            return False
        except Exception as e:
            logger.error("Failed to remove additional cost participant: %s", e)
            return False

    @staticmethod
    def calculate_additional_cost_shares(period_start_date: str) -> dict[str, float]:
        shares: dict[str, float] = {}
        costs = AdditionalCostService.list_additional_costs_by_period(period_start_date)
        participants_by_cost: dict[str, list[AdditionalCostParticipants]] = {}
        for participant in AdditionalCostService.list_participants_by_costs(costs):
            cost = getattr(participant, "additional_cost", None)
            if not cost:
                continue
            participants_by_cost.setdefault(str(cost.id), []).append(participant)  # type: ignore

        for cost in costs:
            participants = participants_by_cost.get(str(cost.id), [])  # type: ignore
            total_weight = sum((p.weight or 0.0) for p in participants)  # type: ignore
            total_amount = cost.total_amount or 0.0  # type: ignore
            if total_weight <= 0 or total_amount <= 0:
                continue
            for participant in participants:
                user = participant.user  # type: ignore
                if not user:
                    continue
                telegram_id = str(user.telegram_id)  # type: ignore
                amount = total_amount * ((participant.weight or 0.0) / total_weight)  # type: ignore
                shares[telegram_id] = shares.get(telegram_id, 0.0) + amount
        return shares


def create_additional_cost(period_start_date: str, name: str, total_amount: float) -> Optional[AdditionalCosts]:
    return AdditionalCostService.create_additional_cost(period_start_date, name, total_amount)


def get_additional_cost(cost_id: str) -> Optional[AdditionalCosts]:
    return AdditionalCostService.get_additional_cost(cost_id)


def update_additional_cost(cost_id: str, **kwargs) -> Optional[AdditionalCosts]:
    return AdditionalCostService.update_additional_cost(cost_id, **kwargs)


def delete_additional_cost(cost_id: str) -> bool:
    return AdditionalCostService.delete_additional_cost(cost_id)


def list_additional_costs_by_period(period_start_date: str) -> List[AdditionalCosts]:
    return AdditionalCostService.list_additional_costs_by_period(period_start_date)


def add_additional_cost_participant(
    cost_id: str,
    user_telegram_id: str,
    weight: float,
) -> Optional[AdditionalCostParticipants]:
    return AdditionalCostService.add_additional_cost_participant(cost_id, user_telegram_id, weight)


def list_additional_cost_participants(cost_id: str) -> List[AdditionalCostParticipants]:
    return AdditionalCostService.list_additional_cost_participants(cost_id)


def list_participants_by_costs(costs: Sequence[AdditionalCosts]) -> List[AdditionalCostParticipants]:
    return AdditionalCostService.list_participants_by_costs(costs)


def delete_additional_cost_participant(participant_id: str) -> bool:
    return AdditionalCostService.delete_additional_cost_participant(participant_id)


def remove_additional_cost_participant(cost_id: str, user_telegram_id: str) -> bool:
    return AdditionalCostService.remove_additional_cost_participant(cost_id, user_telegram_id)


def calculate_additional_cost_shares(period_start_date: str) -> dict[str, float]:
    return AdditionalCostService.calculate_additional_cost_shares(period_start_date)
