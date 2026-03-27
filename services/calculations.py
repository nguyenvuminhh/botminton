"""
Financial calculation logic for sessions and periods.

Session cost per player:
    session_total = venue.price_per_slot × session.slots
    total_weight = Σ (1 + sp.additional_participants) for all participants
    player_cost = (session_total / total_weight) × (1 + player.additional_participants)

Shuttlecock cost per player (period-level):
    total_shuttlecock_cost = Σ batch.total_price for all batches in period
    period_total_weight = Σ player_weight across all sessions in period
    player_shuttlecock_cost = (player_period_weight / period_total_weight) × total_shuttlecock_cost
"""

from datetime import date as dt_date
from typing import Optional
from models.period_money import PeriodMoneyReport, PersonalPeriodMoney
from services.session_participants import SessionParticipantService
from services.sessions import SessionService
from services.periods import PeriodService
from services.shuttlecock_batches import ShuttlecockBatchService
from services.users import UserService
from schemas.sessions import Sessions
from schemas.users import Users
import logging

logger = logging.getLogger(__name__)


class CalculationService:

    @staticmethod
    def calculate_session_costs(session_date: str) -> dict[str, float]:
        """
        Return {telegram_id: amount} for every participant in a session.
        Returns empty dict if session has no venue, no slots, or no participants.
        """
        session = SessionService.get_session_by_date(session_date)
        if not session:
            logger.error(f"Session on {session_date} not found")
            return {}

        if not session.venue or not session.slots:  # type: ignore
            logger.warning(f"Session on {session_date} has no venue or 0 slots — skipping cost calculation")
            return {}

        participants = SessionParticipantService.list_participants_by_session(session_date)
        if not participants:
            return {}

        session_total: float = session.venue.price_per_slot * session.slots  # type: ignore
        total_weight: float = sum(1 + (p.additional_participants or 0) for p in participants)

        if total_weight == 0:
            return {}

        per_unit = session_total / total_weight
        result: dict[str, float] = {}
        for p in participants:
            weight = 1 + (p.additional_participants or 0)
            telegram_id = str(p.user.telegram_id)  # type: ignore
            result[telegram_id] = per_unit * weight

        return result

    @staticmethod
    def calculate_period_report(period_start_date: str) -> Optional[PeriodMoneyReport]:
        """
        Calculate the full money report for a period.
        Each player's total = courts share + shuttlecock share.
        """
        period = PeriodService.get_period_by_start_date(period_start_date)
        if not period:
            logger.error(f"Period starting {period_start_date} not found")
            return None

        sessions = SessionService.list_sessions_by_period_id(period_start_date)

        # --- Courts calculation ---
        player_courts: dict[str, float] = {}
        for session in sessions:
            session_date = session.date.isoformat()  # type: ignore
            costs = CalculationService.calculate_session_costs(session_date)
            for tid, amount in costs.items():
                player_courts[tid] = player_courts.get(tid, 0.0) + amount

        # --- Shuttlecock calculation ---
        total_shuttlecock_cost = ShuttlecockBatchService.get_total_shuttlecock_cost_for_period(period_start_date)

        # Weight = sum of (1 + additional) across ALL sessions attended
        player_period_weight: dict[str, float] = {}
        for session in sessions:
            session_date = session.date.isoformat()  # type: ignore
            participants = SessionParticipantService.list_participants_by_session(session_date)
            for p in participants:
                tid = str(p.user.telegram_id)  # type: ignore
                weight = 1 + (p.additional_participants or 0)
                player_period_weight[tid] = player_period_weight.get(tid, 0.0) + weight

        period_total_weight = sum(player_period_weight.values())

        player_shuttlecock: dict[str, float] = {}
        if period_total_weight > 0 and total_shuttlecock_cost > 0:
            for tid, weight in player_period_weight.items():
                player_shuttlecock[tid] = (weight / period_total_weight) * total_shuttlecock_cost

        # --- Merge ---
        all_player_ids = set(player_courts.keys()) | set(player_shuttlecock.keys())

        personal_entries: list[PersonalPeriodMoney] = []
        for tid in all_player_ids:
            total = player_courts.get(tid, 0.0) + player_shuttlecock.get(tid, 0.0)
            user = UserService.get_user_by_telegram_id(tid)
            username = user.telegram_user_name if user else tid  # type: ignore
            personal_entries.append(
                PersonalPeriodMoney(
                    person_id=tid,
                    telegram_user_name=f"@{username}" if username and not username.startswith("@") else (username or tid),
                    period_money=total,
                )
            )

        personal_entries.sort(key=lambda x: x.period_money, reverse=True)
        total_money = sum(e.period_money for e in personal_entries)

        end_date = period.end_date or dt_date.today()  # type: ignore

        return PeriodMoneyReport(
            period_start_date=period.start_date,  # type: ignore
            period_end_date=end_date,
            period_id=str(period.id),  # type: ignore
            personal_period_money=personal_entries,
            total_period_money=round(total_money, 2),
        )


def calculate_session_costs(session_date: str) -> dict[str, float]:
    return CalculationService.calculate_session_costs(session_date)

def calculate_period_report(period_start_date: str) -> Optional[PeriodMoneyReport]:
    return CalculationService.calculate_period_report(period_start_date)
