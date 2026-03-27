"""
Tests for CalculationService.

Scenario mirrors the spreadsheet example:
  Sessions: 28/2 (slots=2), 7/3 (slots=4), 14/3 (slots=2)
  Venue: 25 €/slot
  Players and weights:
    Hiep:  28/2=1                → courts: 25*2/10*1 = 5.00
    Duy:   28/2=1, 7/3=2        → courts: 5.00 + 100/16*2 = 5+12.5 = 17.50
    Thang: 7/3=1, 14/3=1        → courts: 100/16*1 + 50/8*1 = 6.25+6.25 = 12.50
  Shuttlecock batch: 11.4 €
    period_total_weight = (10 + 16 + 8) = 34  ... simplified scenario below.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.calculations import calculate_session_costs, calculate_period_report
from services.periods import create_period, delete_period
from services.sessions import create_session, delete_session
from services.venues import create_venue, delete_venue
from services.users import create_user, delete_user
from services.session_participants import create_participant, delete_participant_by_user_and_session, update_additional_participants
from services.shuttlecock_batches import create_batch, delete_batch
from utils.database import db_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test identifiers
PERIOD = "2020-06-01"
SESSION_A = "2020-06-05"
SESSION_B = "2020-06-12"
VENUE_NAME = "TestVenue calc"
BATCH_DATE = "2020-06-01"
USER_1 = "calc_user_1"
USER_2 = "calc_user_2"
USER_3 = "calc_user_3"


def setup():
    delete_batch(BATCH_DATE)
    for d in [SESSION_A, SESSION_B]:
        delete_session(d)
    delete_period(PERIOD)
    for u in [USER_1, USER_2, USER_3]:
        delete_user(u)
    delete_venue(VENUE_NAME)


def test_session_cost_calculation():
    try:
        db_manager.connect()
        setup()

        print("\n🧪 Testing Session Cost Calculation")
        print("=" * 45)

        # Setup
        create_user(USER_1, "user1")
        create_user(USER_2, "user2")
        create_user(USER_3, "user3")
        venue = create_venue(VENUE_NAME, "TestLoc", 25.0)
        assert venue is not None

        period = create_period(PERIOD)
        assert period is not None

        # Session A: 2 slots, venue 25€/slot → total 50€
        # User1: weight 1, User2: weight 2 (+1) → total_weight=3
        # User1 share = 50/3 ≈ 16.67, User2 share = 50*2/3 ≈ 33.33
        session_a = create_session(SESSION_A, PERIOD, venue_id=VENUE_NAME, slots=2.0)
        assert session_a is not None

        create_participant(USER_1, SESSION_A, additional_participants=0)
        create_participant(USER_2, SESSION_A, additional_participants=1)  # weight=2

        costs = calculate_session_costs(SESSION_A)
        assert USER_1 in costs
        assert USER_2 in costs
        total_weight = 1 + 2  # 3
        expected_u1 = round(50.0 / total_weight * 1, 10)
        expected_u2 = round(50.0 / total_weight * 2, 10)
        assert abs(costs[USER_1] - expected_u1) < 0.001, f"User1: expected {expected_u1}, got {costs[USER_1]}"
        assert abs(costs[USER_2] - expected_u2) < 0.001, f"User2: expected {expected_u2}, got {costs[USER_2]}"
        print(f"✅ Session costs: user1={costs[USER_1]:.2f}, user2={costs[USER_2]:.2f}")

        # Session B: 4 slots, 25€/slot → total 100€
        # User2: weight 1, User3: weight 1 → each pays 50€
        session_b = create_session(SESSION_B, PERIOD, venue_id=VENUE_NAME, slots=4.0)
        assert session_b is not None
        create_participant(USER_2, SESSION_B, additional_participants=0)
        create_participant(USER_3, SESSION_B, additional_participants=0)

        costs_b = calculate_session_costs(SESSION_B)
        assert abs(costs_b[USER_2] - 50.0) < 0.001
        assert abs(costs_b[USER_3] - 50.0) < 0.001
        print(f"✅ Session B costs: user2={costs_b[USER_2]:.2f}, user3={costs_b[USER_3]:.2f}")

        # Period report
        batch = create_batch(PERIOD, BATCH_DATE, total_price=30.0)  # 30€ shuttlecock
        assert batch is not None

        report = calculate_period_report(PERIOD)
        assert report is not None, "Failed to generate period report"

        # period_total_weight: session_A=(1+2)=3, session_B=(1+1)=2 → total=5
        # User1 weight: 1 (session A only)
        # User2 weight: 2 (session A) + 1 (session B) = 3
        # User3 weight: 1 (session B only)
        # Shuttlecock shares: user1=30*1/5=6, user2=30*3/5=18, user3=30*1/5=6
        # Courts: user1=50/3≈16.67, user2=50*2/3+50=83.33, user3=50
        # Totals: user1≈22.67, user2≈101.33, user3≈56

        by_id = {p.person_id: p.period_money for p in report.personal_period_money}
        assert USER_1 in by_id
        assert USER_2 in by_id
        assert USER_3 in by_id

        expected_u1_total = round(50.0 / 3 * 1 + 30.0 * 1 / 5, 2)
        expected_u2_total = round(50.0 / 3 * 2 + 50.0 + 30.0 * 3 / 5, 2)
        expected_u3_total = round(50.0 + 30.0 * 1 / 5, 2)

        assert abs(by_id[USER_1] - expected_u1_total) < 0.01, f"User1 total: expected {expected_u1_total}, got {by_id[USER_1]}"
        assert abs(by_id[USER_2] - expected_u2_total) < 0.01, f"User2 total: expected {expected_u2_total}, got {by_id[USER_2]}"
        assert abs(by_id[USER_3] - expected_u3_total) < 0.01, f"User3 total: expected {expected_u3_total}, got {by_id[USER_3]}"

        print(f"✅ Period report totals:")
        print(f"   user1={by_id[USER_1]:.2f} (expected {expected_u1_total})")
        print(f"   user2={by_id[USER_2]:.2f} (expected {expected_u2_total})")
        print(f"   user3={by_id[USER_3]:.2f} (expected {expected_u3_total})")

        # Cleanup
        setup()
        print("\n🎉 Calculation tests passed!")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")
        setup()
        raise
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    test_session_cost_calculation()
