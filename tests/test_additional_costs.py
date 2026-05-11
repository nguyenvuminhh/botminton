import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.periods import create_period, delete_period
from services.users import create_user, delete_user
from utils.database import db_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PERIOD = "2020-07-01"
USER_1 = "additional_cost_user_1"
USER_2 = "additional_cost_user_2"


def setup():
    try:
        from schemas.additional_cost_participants import AdditionalCostParticipants
        from schemas.additional_costs import AdditionalCosts

        AdditionalCostParticipants.objects.delete()  # type: ignore
        AdditionalCosts.objects.delete()  # type: ignore
    except Exception:
        pass

    delete_period(PERIOD)
    delete_user(USER_1)
    delete_user(USER_2)


def test_additional_costs_crud():
    try:
        db_manager.connect()
        setup()

        print("\n🧪 Testing Additional Costs CRUD")
        print("=" * 40)

        create_user(USER_1, "extra1")
        create_user(USER_2, "extra2")
        period = create_period(PERIOD)
        assert period is not None

        from services.additional_costs import (
            add_additional_cost_participant,
            create_additional_cost,
            delete_additional_cost,
            list_additional_cost_participants,
            list_additional_costs_by_period,
            remove_additional_cost_participant,
            update_additional_cost,
        )

        cost = create_additional_cost(PERIOD, "Stringing fee", 24.0)
        assert cost is not None
        assert cost.name == "Stringing fee"
        assert cost.total_amount == 24.0

        listed = list_additional_costs_by_period(PERIOD)
        assert len(listed) == 1
        assert str(listed[0].id) == str(cost.id)

        participant_1 = add_additional_cost_participant(str(cost.id), USER_1, 2.0)  # type: ignore
        participant_2 = add_additional_cost_participant(str(cost.id), USER_2, 1.0)  # type: ignore
        assert participant_1 is not None
        assert participant_2 is not None

        updated_participant_1 = add_additional_cost_participant(str(cost.id), USER_1, 3.0)  # type: ignore
        assert updated_participant_1 is not None
        assert updated_participant_1.weight == 3.0

        participants = list_additional_cost_participants(str(cost.id))  # type: ignore
        by_user = {p.user.telegram_id: p.weight for p in participants}  # type: ignore
        assert by_user == {USER_1: 3.0, USER_2: 1.0}

        updated_cost = update_additional_cost(str(cost.id), name="Stringing and tape", total_amount=30.0)  # type: ignore
        assert updated_cost is not None
        assert updated_cost.name == "Stringing and tape"
        assert updated_cost.total_amount == 30.0

        assert remove_additional_cost_participant(str(cost.id), USER_2) is True  # type: ignore
        participants_after_remove = list_additional_cost_participants(str(cost.id))  # type: ignore
        assert len(participants_after_remove) == 1
        assert participants_after_remove[0].user.telegram_id == USER_1  # type: ignore

        assert delete_additional_cost(str(cost.id)) is True  # type: ignore
        assert list_additional_costs_by_period(PERIOD) == []

        setup()
        print("\n🎉 Additional costs CRUD test passed!")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")
        setup()
        raise
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    test_additional_costs_crud()
