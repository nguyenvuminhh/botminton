import { useEffect, useState } from 'react'
import { api } from '../api'

interface Period {
  id: string
  start_date: string
  end_date: string | null
  total_money: number | null
}

export default function Periods() {
  const [periods, setPeriods] = useState<Period[]>([])
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [error, setError] = useState('')

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
    const endDateInput = prompt('End date (YYYY-MM-DD):', new Date().toISOString().split('T')[0])
    if (!endDateInput) return
    await api.put(`/periods/${p.start_date}`, { end_date: endDateInput })
    load()
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
    </div>
  )
}

const inputStyle: React.CSSProperties = { display: 'block', marginTop: 4, padding: '0.4rem 0.6rem', borderRadius: 4, border: '1px solid #cbd5e1', fontSize: 14 }
const btnStyle: React.CSSProperties = { padding: '0.4rem 0.8rem', borderRadius: 4, border: 'none', background: '#3b82f6', color: '#fff', cursor: 'pointer', fontSize: 14 }
const tableStyle: React.CSSProperties = { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }
const thStyle: React.CSSProperties = { textAlign: 'left', padding: '0.75rem 1rem', background: '#f1f5f9', fontSize: 13, color: '#475569' }
const tdStyle: React.CSSProperties = { padding: '0.75rem 1rem', borderTop: '1px solid #f1f5f9', fontSize: 14 }
