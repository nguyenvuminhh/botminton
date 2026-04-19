import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'

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

export default function Home() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [lastClosed, setLastClosed] = useState<Period | null>(null)
  const [currentOpen, setCurrentOpen] = useState<Period | null>(null)
  const [payments, setPayments] = useState<Payment[]>([])
  const [report, setReport] = useState<Report | null>(null)

  const loadPayments = useCallback((startDate: string) => {
    api.get<Payment[]>(`/payments?period=${startDate}`).then((r) => setPayments(r.data)).catch(() => setPayments([]))
  }, [])

  const refresh = useCallback(async () => {
    setLoading(true)
    const { data: periods } = await api.get<Period[]>('/periods')
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
        const r = await api.get<Report>(`/payments/report/${open.start_date}`)
        setReport(r.data)
      } catch {
        setReport(null)
      }
    } else {
      setReport(null)
    }
    setLoading(false)
  }, [])

  useEffect(() => { refresh() }, [refresh])

  async function togglePaid(p: Payment) {
    const endpoint = p.has_paid ? '/payments/mark-unpaid' : '/payments/mark-paid'
    await api.post(endpoint, { period_start_date: p.period_start_date, user_telegram_id: p.user_telegram_id })
    if (lastClosed) loadPayments(lastClosed.start_date)
  }

  if (loading) return <p>Loading…</p>

  const allPaid = payments.length > 0 && payments.every((p) => p.has_paid)

  if (lastClosed && !allPaid) {
    return (
      <div>
        <h2>Home</h2>
        <section style={sectionStyle}>
          <h3 style={h3Style}>
            Unpaid — {lastClosed.start_date} → {lastClosed.end_date}
          </h3>
          <table style={tableStyle}>
            <thead>
              <tr>{['Player', 'Amount', 'Paid'].map((h) => <th key={h} style={thStyle}>{h}</th>)}</tr>
            </thead>
            <tbody>
              {payments.map((p) => (
                <tr key={p.id}>
                  <td style={tdStyle}>{p.user_name ?? p.user_telegram_id}</td>
                  <td style={tdStyle}>€{p.amount.toFixed(2)}</td>
                  <td style={tdStyle}>
                    <label style={{ cursor: 'pointer' }}>
                      <input type="checkbox" checked={p.has_paid} onChange={() => togglePaid(p)} />
                      <span style={{ marginLeft: 6, color: p.has_paid ? '#22c55e' : '#64748b' }}>
                        {p.has_paid ? 'Paid' : 'Unpaid'}
                      </span>
                    </label>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
            <button onClick={() => navigate(`/periods/${lastClosed.start_date}`)} style={btnStyle}>
              Open period →
            </button>
          </div>
        </section>
      </div>
    )
  }

  return (
    <div>
      <h2>Home</h2>

      {lastClosed && allPaid && (
        <div style={{ ...sectionStyle, background: '#ecfdf5', border: '1px solid #a7f3d0' }}>
          <span style={{ color: '#065f46', fontWeight: 600 }}>
            ✓ Previous period ({lastClosed.start_date} → {lastClosed.end_date}) fully paid
          </span>
        </div>
      )}

      {currentOpen ? (
        <section style={sectionStyle}>
          <h3 style={h3Style}>
            Current period preview — {currentOpen.start_date}
            {report && <span style={{ marginLeft: '0.75rem', color: '#64748b', fontWeight: 400 }}>Total: €{report.total_period_money.toFixed(2)}</span>}
          </h3>
          {report && report.personal_period_money.length > 0 ? (
            <table style={tableStyle}>
              <thead>
                <tr>{['Player', 'Amount'].map((h) => <th key={h} style={thStyle}>{h}</th>)}</tr>
              </thead>
              <tbody>
                {report.personal_period_money.map((e) => (
                  <tr key={e.person_id}>
                    <td style={tdStyle}>{e.full_name || e.telegram_user_name}</td>
                    <td style={tdStyle}>€{e.period_money.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p style={{ color: '#64748b' }}>No participants yet in this period.</p>
          )}
          <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
            <button onClick={() => navigate(`/periods/${currentOpen.start_date}`)} style={btnStyle}>
              Open period →
            </button>
          </div>
        </section>
      ) : (
        <p style={{ color: '#64748b' }}>
          No active period — create one from the <a onClick={() => navigate('/periods')} style={{ color: '#3b82f6', cursor: 'pointer' }}>Periods</a> tab.
        </p>
      )}
    </div>
  )
}

const sectionStyle: React.CSSProperties = { background: '#fff', borderRadius: 8, padding: '1.25rem', marginBottom: '1.5rem', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }
const h3Style: React.CSSProperties = { marginTop: 0, marginBottom: '1rem', fontSize: 16 }
const btnStyle: React.CSSProperties = { padding: '0.4rem 0.8rem', borderRadius: 4, border: 'none', background: '#3b82f6', color: '#fff', cursor: 'pointer', fontSize: 14 }
const tableStyle: React.CSSProperties = { width: '100%', borderCollapse: 'collapse', background: '#fff' }
const thStyle: React.CSSProperties = { textAlign: 'left', padding: '0.6rem 0.8rem', background: '#f1f5f9', fontSize: 13, color: '#475569' }
const tdStyle: React.CSSProperties = { padding: '0.5rem 0.8rem', borderTop: '1px solid #f1f5f9', fontSize: 14 }
