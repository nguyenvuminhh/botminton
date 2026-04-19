interface Session {
  id: string
  date: string
  total_money: number
}
interface Participant {
  user_telegram_id: string
  user_name: string | null
  additional_participants: number
}
interface User {
  telegram_id: string
  telegram_user_name: string | null
  full_name: string | null
}
interface Payment {
  user_telegram_id: string
  has_paid: boolean
  amount: number
}
interface ReportEntry {
  person_id: string
  telegram_user_name: string
  full_name: string | null
  period_money: number
}

interface Props {
  sessions: Session[]
  participantsBySession: Record<string, Participant[]>
  shuttlecockTotal: number
  shuttlecockTubes: number
  totalPeriodMoney: number
  personalReport?: ReportEntry[]
  payments?: Payment[]
  users: User[]
  onTogglePaid?: (telegramId: string, hasPaid: boolean) => void
}

function formatShortDate(iso: string) {
  const [, mm, dd] = iso.split('-')
  return `${parseInt(dd)}/${parseInt(mm)}`
}

export default function MoneyMatrix({
  sessions,
  participantsBySession,
  shuttlecockTotal,
  shuttlecockTubes,
  totalPeriodMoney,
  personalReport,
  payments,
  users,
  onTogglePaid,
}: Props) {
  const closed = !!payments && payments.length > 0
  const sessionsSorted = [...sessions].sort((a, b) => (a.date < b.date ? -1 : 1))
  const showShuttlecockCol = shuttlecockTotal > 0 || shuttlecockTubes > 0

  const sessionTotalWeight: Record<string, number> = {}
  for (const s of sessionsSorted) {
    const parts = participantsBySession[s.id] ?? []
    sessionTotalWeight[s.id] = parts.reduce((a, p) => a + 1 + (p.additional_participants || 0), 0)
  }

  type Row = {
    telegramId: string
    name: string
    handle: string | null
    perSession: Record<string, number>
    periodWeight: number
  }
  const rowsMap: Record<string, Row> = {}
  for (const s of sessionsSorted) {
    const parts = participantsBySession[s.id] ?? []
    for (const p of parts) {
      const tid = p.user_telegram_id
      const w = 1 + (p.additional_participants || 0)
      if (!rowsMap[tid]) {
        const u = users.find((x) => x.telegram_id === tid)
        rowsMap[tid] = {
          telegramId: tid,
          name: u?.full_name || u?.telegram_user_name || p.user_name || tid,
          handle: u?.telegram_user_name ?? null,
          perSession: {},
          periodWeight: 0,
        }
      }
      rowsMap[tid].perSession[s.id] = (rowsMap[tid].perSession[s.id] || 0) + w
      rowsMap[tid].periodWeight += w
    }
  }

  const moneyByPlayer: Record<string, number> = {}
  if (closed && payments) {
    for (const p of payments) moneyByPlayer[p.user_telegram_id] = p.amount
  } else if (personalReport) {
    for (const e of personalReport) moneyByPlayer[e.person_id] = e.period_money
  }
  const paidByPlayer: Record<string, boolean> = {}
  if (payments) {
    for (const p of payments) paidByPlayer[p.user_telegram_id] = p.has_paid
  }

  const rows = Object.values(rowsMap)
    .filter((r) => r.periodWeight > 0)
    .sort((a, b) => (moneyByPlayer[b.telegramId] ?? 0) - (moneyByPlayer[a.telegramId] ?? 0))

  const periodTotalWeight = rows.reduce((a, r) => a + r.periodWeight, 0)

  if (rows.length === 0) {
    return <div className="empty-state">No participants yet.</div>
  }

  const sessionColCount = sessionsSorted.length + (showShuttlecockCol ? 1 : 0)
  const shuttleLabel = `${shuttlecockTubes} tube${shuttlecockTubes === 1 ? '' : 's'} of shuttle cock`

  return (
    <div className="table-wrap scroll-x">
      <table className="table table-matrix">
        <thead>
          <tr>
            <th>Player</th>
            <th>Handle</th>
            {sessionsSorted.map((s) => (
              <th key={s.id}>
                <span className="col-header-block">
                  <span className="col-header-title">{formatShortDate(s.date)}</span>
                  <span className="col-header-meta">Price: €{s.total_money.toFixed(2)}</span>
                  <span className="col-header-meta">Shares: {sessionTotalWeight[s.id] || 0}</span>
                </span>
              </th>
            ))}
            {showShuttlecockCol && (
              <th>
                <span className="col-header-block">
                  <span className="col-header-title">{shuttleLabel}</span>
                  <span className="col-header-meta">Price: €{shuttlecockTotal.toFixed(2)}</span>
                  <span className="col-header-meta">Shares: {periodTotalWeight}</span>
                </span>
              </th>
            )}
            <th className="col-total">Total</th>
            {closed && <th>Paid</th>}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.telegramId}>
              <td className="cell-name">{r.name}</td>
              <td className="cell-handle">{r.handle ? '@' + r.handle : '—'}</td>
              {sessionsSorted.map((s) => {
                const w = r.perSession[s.id] || 0
                const cls = 'cell-weight' + (w > 0 ? ' active' : '') + (w > 1 ? ' plus' : '')
                return <td key={s.id} className={cls}>{w > 0 ? w : ''}</td>
              })}
              {showShuttlecockCol && (
                <td className={'cell-weight active' + (r.periodWeight > 1 ? ' plus' : '')}>
                  {r.periodWeight}
                </td>
              )}
              <td className="cell-num cell-money col-total">
                €{(moneyByPlayer[r.telegramId] ?? 0).toFixed(2)}
              </td>
              {closed && (
                <td className="cell-paid">
                  <label className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={paidByPlayer[r.telegramId] ?? false}
                      onChange={() => onTogglePaid?.(r.telegramId, paidByPlayer[r.telegramId] ?? false)}
                    />
                    <span className={'pill ' + (paidByPlayer[r.telegramId] ? 'pill-paid' : 'pill-unpaid')}>
                      {paidByPlayer[r.telegramId] ? 'Paid' : 'Unpaid'}
                    </span>
                  </label>
                </td>
              )}
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <td colSpan={2 + sessionColCount}></td>
            <td className="col-total">€{totalPeriodMoney.toFixed(2)}</td>
            {closed && <td></td>}
          </tr>
        </tfoot>
      </table>
    </div>
  )
}
