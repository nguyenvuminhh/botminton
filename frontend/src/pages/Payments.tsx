import { useEffect, useState } from 'react'
import { api } from '../api'

interface Period { id: string; start_date: string }
interface Payment {
  id: string
  user_telegram_id: string
  user_name: string | null
  amount: number
  has_paid: boolean
  period_start_date: string | null
}
interface ReportEntry { person_id: string; telegram_user_name: string; period_money: number }
interface Report {
  period_start_date: string
  period_end_date: string
  total_period_money: number
  personal_period_money: ReportEntry[]
}

export default function Payments() {
  const [periods, setPeriods] = useState<Period[]>([])
  const [selectedPeriod, setSelectedPeriod] = useState('')
  const [payments, setPayments] = useState<Payment[]>([])
  const [report, setReport] = useState<Report | null>(null)

  useEffect(() => {
    api.get<Period[]>('/periods').then((r) => setPeriods(r.data))
  }, [])

  function loadPayments() {
    if (!selectedPeriod) return
    api.get<Payment[]>(`/payments?period=${selectedPeriod}`).then((r) => setPayments(r.data))
  }

  function loadReport() {
    if (!selectedPeriod) return
    api.get<Report>(`/payments/report/${selectedPeriod}`).then((r) => setReport(r.data)).catch(() => setReport(null))
  }

  useEffect(() => {
    setPayments([]); setReport(null)
    loadPayments()
    loadReport()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedPeriod])

  async function handleMarkPaid(p: Payment) {
    await api.post('/payments/mark-paid', { period_start_date: p.period_start_date, user_telegram_id: p.user_telegram_id })
    loadPayments()
  }

  async function handleMarkUnpaid(p: Payment) {
    await api.post('/payments/mark-unpaid', { period_start_date: p.period_start_date, user_telegram_id: p.user_telegram_id })
    loadPayments()
  }

  async function handleCalculate() {
    loadReport()
  }

  return (
    <div>
      <h2>Payments</h2>
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', alignItems: 'center' }}>
        <label style={{ fontSize: 14 }}>Period:
          <select value={selectedPeriod} onChange={(e) => setSelectedPeriod(e.target.value)} style={inputStyle}>
            <option value="">— select —</option>
            {periods.map((p) => <option key={p.id} value={p.start_date}>{p.start_date}</option>)}
          </select>
        </label>
        {selectedPeriod && <button onClick={handleCalculate} style={btnStyle}>Refresh report</button>}
      </div>

      {report && (
        <div style={{ background: '#fff', borderRadius: 8, padding: '1rem', marginBottom: '1.5rem', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
          <strong>Period report</strong> — Total: <strong>€{report.total_period_money}</strong>
          <ul style={{ marginTop: '0.5rem', paddingLeft: '1.2rem' }}>
            {report.personal_period_money.map((e) => (
              <li key={e.person_id}>{e.telegram_user_name}: €{e.period_money}</li>
            ))}
          </ul>
        </div>
      )}

      <table style={tableStyle}>
        <thead>
          <tr>{['User', 'Amount', 'Paid', ''].map((h) => <th key={h} style={thStyle}>{h}</th>)}</tr>
        </thead>
        <tbody>
          {payments.map((p) => (
            <tr key={p.id}>
              <td style={tdStyle}>{p.user_name ?? p.user_telegram_id}</td>
              <td style={tdStyle}>€{p.amount.toFixed(2)}</td>
              <td style={tdStyle}>{p.has_paid ? '✅ Paid' : '❌ Unpaid'}</td>
              <td style={tdStyle}>
                {p.has_paid
                  ? <button onClick={() => handleMarkUnpaid(p)} style={{ ...btnStyle, background: '#f59e0b' }}>Mark unpaid</button>
                  : <button onClick={() => handleMarkPaid(p)} style={{ ...btnStyle, background: '#22c55e' }}>Mark paid</button>
                }
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

const inputStyle: React.CSSProperties = { padding: '0.4rem 0.6rem', borderRadius: 4, border: '1px solid #cbd5e1', fontSize: 14 }
const btnStyle: React.CSSProperties = { padding: '0.4rem 0.8rem', borderRadius: 4, border: 'none', background: '#3b82f6', color: '#fff', cursor: 'pointer', fontSize: 14 }
const tableStyle: React.CSSProperties = { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }
const thStyle: React.CSSProperties = { textAlign: 'left', padding: '0.75rem 1rem', background: '#f1f5f9', fontSize: 13, color: '#475569' }
const tdStyle: React.CSSProperties = { padding: '0.75rem 1rem', borderTop: '1px solid #f1f5f9', fontSize: 14 }
