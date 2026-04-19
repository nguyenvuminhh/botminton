from datetime import datetime, timezone

from schemas.periods import Periods
from services.calculations import calculate_period_report
from services.period_shuttlecock_uses import list_uses_by_period
from services.session_participants import list_session_participants
from services.sessions import list_sessions_by_period
from services.users import list_all_users


def build_period_matrix(period: Periods) -> dict:
    start_date_iso = period.start_date.isoformat()  # type: ignore
    sessions = list_sessions_by_period(start_date_iso)

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
        parts = list_session_participants(sdate) if sdate else []
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

    all_users = list_all_users(limit=10000)
    users_out = []
    for u in all_users:
        tid = str(u.telegram_id)  # type: ignore
        if tid not in user_ids:
            continue
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
        "total_period_money": total_money,
        "personal_report": personal,
        "users": users_out,
        "snapshot_at": datetime.now(timezone.utc).isoformat(),
    }
