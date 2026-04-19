import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import MoneyMatrix from '../components/MoneyMatrix'

interface Period {
  id: string
  start_date: string
  end_date: string | null
  total_money: number | null
}
interface Payment {
  id: string
  user_telegram_id: string
  user_name: string | null
  amount: number
  has_paid: boolean
  period_start_date: string | null
}
interface ReportEntry { person_id: string; telegram_user_name: string; full_name: string | null; period_money: number }
interface Report {
  period_start_date: string
  period_end_date: string
  total_period_money: number
  personal_period_money: ReportEntry[]
}
interface Session {
  id: string
  date: string
  venue_name: string | null
  slots: number
  people_count: number
  total_money: number
  is_poll_open: boolean
}
interface Participant {
  id: string
  user_telegram_id: string
  user_name: string | null
  additional_participants: number
}
interface User {
  id: string
  telegram_id: string
  telegram_user_name: string | null
  full_name: string | null
}
interface ShuttlecockUse {
  id: string
  price_each: number
  tubes_used: number
}

export default function Home() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [lastClosed, setLastClosed] = useState<Period | null>(null)
  const [currentOpen, setCurrentOpen] = useState<Period | null>(null)
  const [payments, setPayments] = useState<Payment[]>([])
  const [report, setReport] = useState<Report | null>(null)
  const [sessions, setSessions] = useState<Session[]>([])
  const [participantsBySession, setParticipantsBySession] = useState<Record<string, Participant[]>>({})
  const [shuttlecockTotal, setShuttlecockTotal] = useState(0)
  const [shuttlecockTubes, setShuttlecockTubes] = useState(0)
  const [users, setUsers] = useState<User[]>([])

  const loadPayments = useCallback((startDate: string) => {
    api.get<Payment[]>(`/payments?period=${startDate}`).then((r) => setPayments(r.data)).catch(() => setPayments([]))
  }, [])

  const refresh = useCallback(async () => {
    setLoading(true)
    const [{ data: periods }, { data: usersList }] = await Promise.all([
      api.get<Period[]>('/periods'),
      api.get<User[]>('/users'),
    ])
    setUsers(usersList)

    const closed = periods
      .filter((p) => p.end_date)
      .sort((a, b) => (a.end_date! < b.end_date! ? 1 : -1))[0] ?? null
    const open = periods
      .filter((p) => !p.end_date)
      .sort((a, b) => (a.start_date < b.start_date ? 1 : -1))[0] ?? null
    setLastClosed(closed)
    setCurrentOpen(open)

    if (closed) {
      const r = await api.get<Payment[]>(`/payments?period=${closed.start_date}`)
      setPayments(r.data)
    } else {
      setPayments([])
    }

    if (open) {
      try {
        const [reportRes, sessionsRes, usesRes] = await Promise.all([
          api.get<Report>(`/payments/report/${open.start_date}`),
          api.get<Session[]>(`/sessions?period=${open.start_date}`),
          api.get<ShuttlecockUse[]>(`/periods/${open.start_date}/shuttlecocks`),
        ])
        setReport(reportRes.data)
        setSessions(sessionsRes.data)
        setShuttlecockTotal(usesRes.data.reduce((a, u) => a + u.price_each * u.tubes_used, 0))
        setShuttlecockTubes(usesRes.data.reduce((a, u) => a + u.tubes_used, 0))

        const partResults = await Promise.all(
          sessionsRes.data.map((s) =>
            api.get<Participant[]>(`/participants?session_date=${s.date}`).then((r) => [s.id, r.data] as const)
          )
        )
        setParticipantsBySession(Object.fromEntries(partResults))
      } catch {
        setReport(null)
        setSessions([])
        setParticipantsBySession({})
        setShuttlecockTotal(0)
        setShuttlecockTubes(0)
      }
    } else {
      setReport(null)
      setSessions([])
      setParticipantsBySession({})
      setShuttlecockTotal(0)
      setShuttlecockTubes(0)
    }
    setLoading(false)
  }, [])

  useEffect(() => { refresh() }, [refresh])

  async function togglePaid(p: Payment) {
    const endpoint = p.has_paid ? '/payments/mark-unpaid' : '/payments/mark-paid'
    await api.post(endpoint, { period_start_date: p.period_start_date, user_telegram_id: p.user_telegram_id })
    if (lastClosed) loadPayments(lastClosed.start_date)
  }

  if (loading) {
    return (
      <>
        <div className="page-header"><h1>Home</h1></div>
        <div className="card empty-state">Loading…</div>
      </>
    )
  }

  const allPaid = payments.length > 0 && payments.every((p) => p.has_paid)
  const unpaidCount = payments.filter((p) => !p.has_paid).length
  const unpaidTotal = payments.filter((p) => !p.has_paid).reduce((a, p) => a + p.amount, 0)

  if (lastClosed && !allPaid) {
    return (
      <>
        <div className="page-header">
          <h1>Home</h1>
          <span className="page-subtitle">Outstanding payments need your attention.</span>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Unpaid — {lastClosed.start_date} → {lastClosed.end_date}</h3>
            <span className="chip">
              {unpaidCount} unpaid · €{unpaidTotal.toFixed(2)}
            </span>
            <div className="card-header-actions">
              <button className="btn btn-primary btn-sm" onClick={() => navigate(`/periods/${lastClosed.start_date}`)}>
                Open period →
              </button>
            </div>
          </div>

          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr><th>Player</th><th className="cell-num">Amount</th><th>Status</th></tr>
              </thead>
              <tbody>
                {payments.map((p) => (
                  <tr key={p.id}>
                    <td>{p.user_name ?? p.user_telegram_id}</td>
                    <td className="cell-num cell-money">€{p.amount.toFixed(2)}</td>
                    <td>
                      <label className="checkbox-row">
                        <input type="checkbox" checked={p.has_paid} onChange={() => togglePaid(p)} />
                        <span className={'pill ' + (p.has_paid ? 'pill-paid' : 'pill-unpaid')}>
                          {p.has_paid ? 'Paid' : 'Unpaid'}
                        </span>
                      </label>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </>
    )
  }

  return (
    <>
      <div className="page-header">
        <h1>Home</h1>
        <span className="page-subtitle">Overview of the current period.</span>
      </div>

      {lastClosed && allPaid && (
        <div className="card card-success">
          ✓ Previous period ({lastClosed.start_date} → {lastClosed.end_date}) fully paid
        </div>
      )}

      {currentOpen ? (
        <div className="card">
          <div className="card-header">
            <h3>Current period preview</h3>
            <span className="chip">from {currentOpen.start_date}</span>
            {report && (
              <span className="pill pill-accent">
                Total €{report.total_period_money.toFixed(2)}
              </span>
            )}
            <div className="card-header-actions">
              <button className="btn btn-primary btn-sm" onClick={() => navigate(`/periods/${currentOpen.start_date}?close=1`)}>
                Close period →
              </button>
            </div>
          </div>

          <MoneyMatrix
            sessions={sessions}
            participantsBySession={participantsBySession}
            shuttlecockTotal={shuttlecockTotal}
            shuttlecockTubes={shuttlecockTubes}
            totalPeriodMoney={report?.total_period_money ?? 0}
            personalReport={report?.personal_period_money}
            users={users}
          />
        </div>
      ) : (
        <div className="card empty-state">
          No active period — create one from the{' '}
          <a onClick={() => navigate('/periods')} style={{ cursor: 'pointer' }}>Periods</a> tab.
        </div>
      )}
    </>
  )
}
