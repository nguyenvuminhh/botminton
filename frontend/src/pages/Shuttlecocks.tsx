import { useEffect, useState } from 'react'
import { api } from '../api'

interface Period { id: string; start_date: string }
interface Batch {
  id: string
  purchase_date: string
  total_price: number
  tube_count: number | null
  period_start_date: string | null
}

export default function Shuttlecocks() {
  const [periods, setPeriods] = useState<Period[]>([])
  const [selectedPeriod, setSelectedPeriod] = useState('')
  const [batches, setBatches] = useState<Batch[]>([])
  const [purchaseDate, setPurchaseDate] = useState('')
  const [price, setPrice] = useState('')
  const [tubeCount, setTubeCount] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    api.get<Period[]>('/periods').then((r) => setPeriods(r.data))
  }, [])

  function load() {
    if (!selectedPeriod) return
    api.get<Batch[]>(`/shuttlecocks?period=${selectedPeriod}`).then((r) => setBatches(r.data))
  }

  useEffect(() => { setBatches([]); load() }, [selectedPeriod])

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    try {
      await api.post('/shuttlecocks', {
        period_start_date: selectedPeriod,
        purchase_date: purchaseDate,
        total_price: parseFloat(price),
        tube_count: tubeCount ? parseInt(tubeCount) : undefined,
      })
      setPurchaseDate(''); setPrice(''); setTubeCount('')
      load()
    } catch {
      setError('Failed to add batch')
    }
  }

  async function handleDelete(pd: string) {
    if (!confirm(`Delete batch on ${pd}?`)) return
    await api.delete(`/shuttlecocks/${pd}`)
    load()
  }

  const total = batches.reduce((s, b) => s + b.total_price, 0)

  return (
    <div>
      <h2>Shuttlecock Batches</h2>
      <div style={{ marginBottom: '1rem' }}>
        <label style={{ fontSize: 14 }}>Period:
          <select value={selectedPeriod} onChange={(e) => setSelectedPeriod(e.target.value)} style={inputStyle}>
            <option value="">— select —</option>
            {periods.map((p) => <option key={p.id} value={p.start_date}>{p.start_date}</option>)}
          </select>
        </label>
      </div>

      {selectedPeriod && (
        <form onSubmit={handleAdd} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
          <input type="date" value={purchaseDate} onChange={(e) => setPurchaseDate(e.target.value)} required style={inputStyle} />
          <input type="number" step="0.01" placeholder="Total price (€)" value={price} onChange={(e) => setPrice(e.target.value)} required style={{ ...inputStyle, width: 160 }} />
          <input type="number" placeholder="Tube count" value={tubeCount} onChange={(e) => setTubeCount(e.target.value)} style={{ ...inputStyle, width: 120 }} />
          <button type="submit" style={btnStyle}>Add Batch</button>
        </form>
      )}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {batches.length > 0 && (
        <p style={{ marginBottom: '0.75rem', fontWeight: 600 }}>Total: €{total.toFixed(2)}</p>
      )}

      <table style={tableStyle}>
        <thead>
          <tr>{['Purchase date', 'Price', 'Tubes', ''].map((h) => <th key={h} style={thStyle}>{h}</th>)}</tr>
        </thead>
        <tbody>
          {batches.map((b) => (
            <tr key={b.id}>
              <td style={tdStyle}>{b.purchase_date}</td>
              <td style={tdStyle}>€{b.total_price.toFixed(2)}</td>
              <td style={tdStyle}>{b.tube_count ?? '—'}</td>
              <td style={tdStyle}>
                <button onClick={() => handleDelete(b.purchase_date)} style={{ ...btnStyle, background: '#ef4444' }}>Delete</button>
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
