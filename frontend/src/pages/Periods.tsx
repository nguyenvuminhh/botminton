import { useEffect, useState } from 'react'
import { api } from '../api'

interface Period {
  id: string
  start_date: string
  end_date: string | null
  total_money: number | null
}

interface ReportEntry {
  person_id: string
  telegram_user_name: string
  full_name: string | null
  period_money: number
}

interface Report {
  period_start_date: string
  period_end_date: string
  total_period_money: number
  personal_period_money: ReportEntry[]
}

function todayISO(): string {
  return new Date().toISOString().split('T')[0]
}

function tomorrowISO(): string {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  return d.toISOString().split('T')[0]
}

export default function Periods() {
  const [periods, setPeriods] = useState<Period[]>([])
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [error, setError] = useState('')

  // close-preview modal state
  const [previewPeriod, setPreviewPeriod] = useState<Period | null>(null)
  const [report, setReport] = useState<Report | null>(null)
  const [reportLoading, setReportLoading] = useState(false)
  const [closeEndDate, setCloseEndDate] = useState('')
  const [newStartDate, setNewStartDate] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [modalError, setModalError] = useState('')

  function load() {
    api.get<Period[]>('/periods').then((r) => setPeriods(r.data))
  }

  useEffect(() => { load() }, [])

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    try {
      await api.post('/periods', { start_date: startDate, end_date: endDate || null })
      setStartDate(''); setEndDate('')
      load()
    } catch {
      setError('Failed to create period')
    }
  }

  async function handleClose(p: Period) {
    setPreviewPeriod(p)
    setReport(null)
    setModalError('')
    setCloseEndDate(todayISO())
    setNewStartDate(tomorrowISO())
    setReportLoading(true)
    try {
      const r = await api.get<Report>(`/payments/report/${p.start_date}`)
      setReport(r.data)
    } catch {
      setReport({ period_start_date: p.start_date, period_end_date: todayISO(), total_period_money: 0, personal_period_money: [] })
    } finally {
      setReportLoading(false)
    }
  }

  function closeModal() {
    setPreviewPeriod(null)
    setReport(null)
    setModalError('')
  }

  async function handleFinalize() {
    if (!previewPeriod) return
    setSubmitting(true)
    setModalError('')
    try {
      await api.post(`/periods/${previewPeriod.start_date}/finalize`, {
        end_date: closeEndDate,
        new_period_start_date: newStartDate,
      })
      closeModal()
      load()
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setModalError(msg || 'Failed to finalize period')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(startDate: string) {
    if (!confirm(`Delete period starting ${startDate}? This will cascade to sessions!`)) return
    await api.delete(`/periods/${startDate}`)
    load()
  }

  return (
    <div>
      <h2>Periods</h2>
      <form onSubmit={handleAdd} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <label style={{ fontSize: 13, color: '#475569' }}>Start date:
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} required style={inputStyle} />
        </label>
        <label style={{ fontSize: 13, color: '#475569' }}>End date (optional):
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} style={inputStyle} />
        </label>
        <button type="submit" style={{ ...btnStyle, alignSelf: 'flex-end' }}>Add Period</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <table style={tableStyle}>
        <thead>
          <tr>{['Start', 'End', 'Total €', ''].map((h) => <th key={h} style={thStyle}>{h}</th>)}</tr>
        </thead>
        <tbody>
          {periods.map((p) => (
            <tr key={p.id}>
              <td style={tdStyle}>{p.start_date}</td>
              <td style={tdStyle}>{p.end_date ?? <em style={{ color: '#94a3b8' }}>open</em>}</td>
              <td style={tdStyle}>{p.total_money != null ? `€${p.total_money}` : '—'}</td>
              <td style={{ ...tdStyle, display: 'flex', gap: '0.4rem' }}>
                {!p.end_date && (
                  <button onClick={() => handleClose(p)} style={btnStyle}>Close</button>
                )}
                <button onClick={() => handleDelete(p.start_date)} style={{ ...btnStyle, background: '#ef4444' }}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {previewPeriod && (
        <div
          onClick={closeModal}
          style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50,
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: '#fff', borderRadius: 8, padding: '1.5rem',
              width: '100%', maxWidth: 520, maxHeight: '90vh', overflowY: 'auto',
              boxShadow: '0 8px 24px rgba(0,0,0,0.2)',
            }}
          >
            <h3 style={{ marginTop: 0 }}>Close period {previewPeriod.start_date}</h3>

            {reportLoading && <p style={{ color: '#64748b' }}>Calculating report…</p>}

            {report && !reportLoading && (
              <div style={{ marginBottom: '1rem' }}>
                {report.personal_period_money.length === 0 ? (
                  <p style={{ color: '#64748b', fontSize: 14 }}>No participants in this period — nothing to charge.</p>
                ) : (
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
                      <tr>
                        <td style={{ ...tdStyle, fontWeight: 700 }}>Total</td>
                        <td style={{ ...tdStyle, fontWeight: 700 }}>€{report.total_period_money.toFixed(2)}</td>
                      </tr>
                    </tbody>
                  </table>
                )}
              </div>
            )}

            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
              <label style={{ fontSize: 13, color: '#475569' }}>End date
                <input type="date" value={closeEndDate} onChange={(e) => setCloseEndDate(e.target.value)} style={inputStyle} />
              </label>
              <label style={{ fontSize: 13, color: '#475569' }}>New period start
                <input type="date" value={newStartDate} onChange={(e) => setNewStartDate(e.target.value)} style={inputStyle} />
              </label>
            </div>

            {modalError && <p style={{ color: '#ef4444', fontSize: 14 }}>{modalError}</p>}

            <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
              <button onClick={closeModal} style={{ ...btnStyle, background: '#94a3b8' }} disabled={submitting}>Cancel</button>
              <button
                onClick={handleFinalize}
                style={btnStyle}
                disabled={submitting || reportLoading || !closeEndDate || !newStartDate}
              >
                {submitting ? 'Sending…' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

const inputStyle: React.CSSProperties = { display: 'block', marginTop: 4, padding: '0.4rem 0.6rem', borderRadius: 4, border: '1px solid #cbd5e1', fontSize: 14 }
const btnStyle: React.CSSProperties = { padding: '0.4rem 0.8rem', borderRadius: 4, border: 'none', background: '#3b82f6', color: '#fff', cursor: 'pointer', fontSize: 14 }
const tableStyle: React.CSSProperties = { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }
const thStyle: React.CSSProperties = { textAlign: 'left', padding: '0.75rem 1rem', background: '#f1f5f9', fontSize: 13, color: '#475569' }
const tdStyle: React.CSSProperties = { padding: '0.75rem 1rem', borderTop: '1px solid #f1f5f9', fontSize: 14 }
