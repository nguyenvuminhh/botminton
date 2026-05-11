from datetime import date
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from services import calculations


class CalculatePeriodReportBatchingTest(unittest.TestCase):
    def test_period_report_batches_participants_without_per_session_recalculation(self):
        period = SimpleNamespace(
            id="period-1",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        venue = SimpleNamespace(price_per_slot=10.0)
        user_1 = SimpleNamespace(
            telegram_id="u1",
            telegram_user_name="player_one",
            full_name="Player One",
        )
        user_2 = SimpleNamespace(
            telegram_id="u2",
            telegram_user_name="player_two",
            full_name="Player Two",
        )
        session_1 = SimpleNamespace(id="s1", date=date(2024, 1, 8), venue=venue, slots=2.0)
        session_2 = SimpleNamespace(id="s2", date=date(2024, 1, 15), venue=venue, slots=3.0)
        participants = [
            SimpleNamespace(session=session_1, user=user_1, additional_participants=0),
            SimpleNamespace(session=session_1, user=user_2, additional_participants=0),
            SimpleNamespace(session=session_2, user=user_1, additional_participants=1),
            SimpleNamespace(session=session_2, user=user_2, additional_participants=0),
        ]

        with (
            patch.object(calculations.PeriodService, "get_period_by_start_date", return_value=period),
            patch.object(calculations.SessionService, "list_sessions_by_period_id", return_value=[session_1, session_2]),
            patch.object(
                calculations.SessionParticipantService,
                "list_participants_by_sessions",
                return_value=participants,
                create=True,
            ) as list_participants_by_sessions,
            patch.object(calculations.ShuttlecockBatchService, "get_total_shuttlecock_cost_for_period", return_value=0.0),
            patch.object(
                calculations.UserService,
                "list_users_by_telegram_ids",
                return_value=[user_1, user_2],
                create=True,
            ),
            patch.object(calculations, "calculate_additional_cost_shares", return_value={}),
            patch.object(
                calculations.CalculationService,
                "calculate_session_costs",
                side_effect=AssertionError("period report should not recalculate each session"),
            ),
        ):
            report = calculations.calculate_period_report("2024-01-01")

        self.assertIsNotNone(report)
        list_participants_by_sessions.assert_called_once_with([session_1, session_2])

        by_id = {entry.person_id: entry.period_money for entry in report.personal_period_money}
        self.assertAlmostEqual(by_id["u1"], 30.0)
        self.assertAlmostEqual(by_id["u2"], 20.0)


if __name__ == "__main__":
    unittest.main()
