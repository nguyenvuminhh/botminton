import os
import sys
from datetime import date as dt_date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas.periods import Periods
from services.periods import PeriodService, create_period


def test_create_period_assigns_unique_share_token_before_save():
    original_get_period = PeriodService.get_period_by_start_date
    original_save = Periods.save
    saved_tokens: list[str | None] = []

    try:
        PeriodService.get_period_by_start_date = staticmethod(lambda start_date: None)

        def fake_save(self, *args, **kwargs):
            saved_tokens.append(self.share_token)  # type: ignore[attr-defined]
            return self

        Periods.save = fake_save  # type: ignore[method-assign]

        first = create_period("2031-01-01")
        second = create_period("2031-01-08")

        assert first is not None
        assert second is not None
        assert first.start_date == dt_date.fromisoformat("2031-01-01")
        assert second.start_date == dt_date.fromisoformat("2031-01-08")
        assert first.share_token  # type: ignore[attr-defined]
        assert second.share_token  # type: ignore[attr-defined]
        assert first.share_token != second.share_token  # type: ignore[attr-defined]
        assert saved_tokens == [first.share_token, second.share_token]  # type: ignore[attr-defined]
    finally:
        PeriodService.get_period_by_start_date = staticmethod(original_get_period)
        Periods.save = original_save  # type: ignore[method-assign]


if __name__ == "__main__":
    test_create_period_assigns_unique_share_token_before_save()
