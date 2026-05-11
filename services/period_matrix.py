from datetime import datetime, timezone

from models.period_money import PeriodMoneyReport
from schemas.periods import Periods
from services.additional_costs import list_additional_costs_by_period, list_participants_by_costs
from services.calculations import calculate_period_report
from services.period_shuttlecock_uses import list_uses_by_period
from services.session_participants import list_participants_by_sessions
from services.sessions import list_sessions_by_period
from services.users import list_users_by_telegram_ids


def build_period_matrix(period: Periods, report: PeriodMoneyReport | None = None) -> dict:
    start_date_iso = period.start_date.isoformat()  # type: ignore
    sessions = list_sessions_by_period(start_date_iso)
    participants = list_participants_by_sessions(sessions)
    participants_by_session: dict[str, list] = {}
    for p in participants:
        session = getattr(p, "session", None)
        if not session:
            continue
        participants_by_session.setdefault(str(session.id), []).append(p)  # type: ignore

    sessions_out = []
    participants_out: dict[str, list[dict]] = {}
    user_ids: set[str] = set()
    for s in sessions:
        price_per_slot = s.venue.price_per_slot if s.venue else 0.0  # type: ignore
        slots = s.slots or 0.0  # type: ignore
        total_money = round(price_per_slot * slots, 2) if price_per_slot and slots else 0.0
        sid = str(s.id)  # type: ignore
        sdate = s.date.isoformat() if s.date else None  # type: ignore
        sessions_out.append({
            "id": sid,
            "date": sdate,
            "total_money": total_money,
        })
        parts = participants_by_session.get(sid, [])
        items = []
        for p in parts:
            tid = str(p.user.telegram_id) if p.user else None  # type: ignore
            if not tid:
                continue
            user_ids.add(tid)
            items.append({
                "user_telegram_id": tid,
                "user_name": p.user.telegram_user_name if p.user else None,  # type: ignore
                "additional_participants": p.additional_participants or 0,  # type: ignore
            })
        participants_out[sid] = items

    uses = list_uses_by_period(start_date_iso)
    shuttlecock_total = 0.0
    shuttlecock_tubes = 0
    for u in uses:
        batch = u.batch  # type: ignore
        if not batch:
            continue
        tube_count = batch.tube_count or 0  # type: ignore
        total_price = batch.total_price or 0.0  # type: ignore
        price_each = (total_price / tube_count) if tube_count else 0.0
        tubes_used = u.tubes_used or 0  # type: ignore
        shuttlecock_total += price_each * tubes_used
        shuttlecock_tubes += tubes_used
    shuttlecock_total = round(shuttlecock_total, 2)

    additional_costs_out = []
    additional_cost_participants_out: dict[str, list[dict]] = {}
    additional_costs = list_additional_costs_by_period(start_date_iso)
    participants_by_cost: dict[str, list] = {}
    for p in list_participants_by_costs(additional_costs):
        cost = getattr(p, "additional_cost", None)
        if not cost:
            continue
        participants_by_cost.setdefault(str(cost.id), []).append(p)  # type: ignore

    for cost in additional_costs:
        cost_id = str(cost.id)  # type: ignore
        participants_for_cost = participants_by_cost.get(cost_id, [])
        total_weight = sum((p.weight or 0.0) for p in participants_for_cost)  # type: ignore
        additional_costs_out.append({
            "id": cost_id,
            "name": cost.name,  # type: ignore
            "total_amount": cost.total_amount,  # type: ignore
            "total_weight": total_weight,
        })
        items = []
        for p in participants_for_cost:
            tid = str(p.user.telegram_id) if p.user else None  # type: ignore
            if not tid:
                continue
            user_ids.add(tid)
            items.append({
                "user_telegram_id": tid,
                "user_name": p.user.telegram_user_name if p.user else None,  # type: ignore
                "full_name": p.user.full_name if p.user else None,  # type: ignore
                "weight": p.weight or 0.0,  # type: ignore
            })
        additional_cost_participants_out[cost_id] = items

    if report is None:
        report = calculate_period_report(start_date_iso)
    personal = []
    total_money = 0.0
    if report:
        total_money = report.total_period_money
        for e in report.personal_period_money:
            personal.append({
                "person_id": e.person_id,
                "telegram_user_name": e.telegram_user_name,
                "full_name": e.full_name,
                "period_money": e.period_money,
            })
            user_ids.add(e.person_id)

    users_out = []
    for u in list_users_by_telegram_ids(list(user_ids)):
        tid = str(u.telegram_id)  # type: ignore
        users_out.append({
            "telegram_id": tid,
            "telegram_user_name": u.telegram_user_name,  # type: ignore
            "full_name": u.full_name,  # type: ignore
        })

    return {
        "period": {
            "start_date": start_date_iso,
            "end_date": period.end_date.isoformat() if period.end_date else None,  # type: ignore
        },
        "sessions": sessions_out,
        "participants_by_session": participants_out,
        "shuttlecock_total": shuttlecock_total,
        "shuttlecock_tubes": shuttlecock_tubes,
        "additional_costs": additional_costs_out,
        "additional_cost_participants_by_cost": additional_cost_participants_out,
        "total_period_money": total_money,
        "personal_report": personal,
        "users": users_out,
        "snapshot_at": datetime.now(timezone.utc).isoformat(),
    }
