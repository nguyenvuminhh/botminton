import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import MoneyMatrix from '../components/MoneyMatrix'
import type { MatrixPayload } from '../matrix'

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
export default function Home() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [lastClosed, setLastClosed] = useState<Period | null>(null)
  const [currentOpen, setCurrentOpen] = useState<Period | null>(null)
  const [payments, setPayments] = useState<Payment[]>([])
  const [matrix, setMatrix] = useState<MatrixPayload | null>(null)
  const [summaryLoading, setSummaryLoading] = useState(false)
  const [error, setError] = useState('')
  const [summaryError, setSummaryError] = useState('')

  const refresh = useCallback(async () => {
    setError(''); setSummaryError('')
    const { data: periods } = await api.get<Period[]>('/periods')
    const closed = periods
      .filter((p) => p.end_date)
      .sort((a, b) => (a.end_date! < b.end_date! ? 1 : -1))[0] ?? null
    const open = periods
      .filter((p) => !p.end_date)
      .sort((a, b) => (a.start_date < b.start_date ? 1 : -1))[0] ?? null
    setLastClosed(closed)
    setCurrentOpen(open)

    // Show payment status immediately; fetch the summary only when it is visible.
    if (closed) {
      const { data } = await api.get<Payment[]>(`/payments?period=${closed.start_date}`)
      setPayments(data)
      if (data.some((p) => !p.has_paid)) { setLoading(false); return }
    } else { setPayments([]) }
    setLoading(false)
    if (open) {
      setSummaryLoading(true)
      try {
        const { data } = await api.get<MatrixPayload>(`/periods/${open.start_date}/matrix`)
        setMatrix(data)
      } catch { setSummaryError('Could not load the period summary.') }
      finally { setSummaryLoading(false) }
    }

  }, [])

  useEffect(() => {
    Promise.resolve()
      .then(refresh)
      .catch(() => { setError('Could not load the home page.'); setLoading(false) })
  }, [refresh])

  async function togglePaid(p: Payment) {
    const endpoint = p.has_paid ? '/payments/mark-unpaid' : '/payments/mark-paid'
    await api.post(endpoint, { period_start_date: p.period_start_date, user_telegram_id: p.user_telegram_id })
    const { data } = await api.get<Payment[]>(`/payments?period=${p.period_start_date}`)
    setPayments(data)
    if (data.every((payment) => payment.has_paid)) await refresh()
  }

  if (loading) {
    return (
      <>
        <div className="page-header"><h1>Home</h1></div>
        <div className="card empty-state">Loading…</div>
      </>
    )
  }

  if (error) return <div className="card"><p role="alert">{error}</p><button className="btn btn-primary" onClick={() => void refresh().catch(() => setError('Could not load the home page.'))}>Retry</button></div>

  const allPaid = payments.every((p) => p.has_paid)
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
            {matrix && (
              <span className="pill pill-accent">
                Total €{matrix.total_period_money.toFixed(2)}
              </span>
            )}
            <div className="card-header-actions">
              <button className="btn btn-primary btn-sm" onClick={() => navigate(`/periods/${currentOpen.start_date}?close=1`)}>
                Close period →
              </button>
            </div>
          </div>

          {summaryLoading && <div className="empty-state" role="status">Loading period summary…</div>}
          {summaryError && <div className="error-banner" role="alert">{summaryError} <button className="btn btn-sm btn-ghost" onClick={() => void refresh().catch(() => setError('Could not load the home page.'))}>Retry</button></div>}
          {matrix && !summaryLoading && !summaryError && <MoneyMatrix
            sessions={matrix.sessions}
            participantsBySession={matrix.participants_by_session}
            shuttlecockTotal={matrix.shuttlecock_total}
            shuttlecockTubes={matrix.shuttlecock_tubes}
            additionalCosts={matrix.additional_costs}
            additionalCostParticipantsByCost={matrix.additional_cost_participants_by_cost}
            totalPeriodMoney={matrix.total_period_money}
            personalReport={matrix.personal_report}
            users={matrix.users}
          />}
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
