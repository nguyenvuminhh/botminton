import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
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
  const [error, setError] = useState('')
  const navigate = useNavigate()

  function load() {
    api.get<Period[]>('/periods').then((r) => setPeriods(r.data))
  }

  useEffect(() => { load() }, [])

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    try {
      await api.post('/periods', { start_date: startDate })
      setStartDate('')
      load()
    } catch {
      setError('Failed to create period')
    }
  }

  return (
    <>
      <div className="page-header">
        <h1>Periods</h1>
        <span className="page-subtitle">{periods.length} period{periods.length === 1 ? '' : 's'}</span>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>New period</h3>
        </div>
        <form onSubmit={handleAdd} className="form-row">
          <div className="field">
            <label className="field-label">Start date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              required
              className="input"
            />
          </div>
          <button type="submit" className="btn btn-primary">Add period</button>
        </form>
        {error && <div className="error-banner" style={{ marginTop: 14, marginBottom: 0 }}>{error}</div>}
      </div>

      <div className="card" style={{ padding: 0 }}>
        <div className="table-wrap" style={{ border: 'none', borderRadius: 'inherit' }}>
          <table className="table">
            <thead>
              <tr>
                <th>Start</th>
                <th>End</th>
                <th className="cell-num">Total</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {periods.map((p) => (
                <tr
                  key={p.id}
                  onClick={() => navigate(`/periods/${p.start_date}`)}
                  className="row-clickable"
                >
                  <td>{p.start_date}</td>
                  <td>{p.end_date ?? <span className="muted">—</span>}</td>
                  <td className="cell-num cell-money">
                    {p.total_money != null ? `€${p.total_money}` : <span className="muted">—</span>}
                  </td>
                  <td>
                    <span className={'pill ' + (p.end_date ? 'pill-closed' : 'pill-open')}>
                      {p.end_date ? 'Closed' : 'Open'}
                    </span>
                  </td>
                </tr>
              ))}
              {periods.length === 0 && (
                <tr><td colSpan={4} className="muted" style={{ textAlign: 'center', padding: 32 }}>No periods yet.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  )
}
