import { useEffect, useState } from 'react'
import { api } from '../api'

interface Batch {
  id: string
  purchase_date: string
  total_price: number
  tube_count: number
  price_each: number
  consumed: number
  remaining: number
}

export default function Shuttlecocks() {
  const [batches, setBatches] = useState<Batch[]>([])
  const [purchaseDate, setPurchaseDate] = useState('')
  const [totalPrice, setTotalPrice] = useState('')
  const [tubeCount, setTubeCount] = useState('')
  const [error, setError] = useState('')

  function load() {
    api.get<Batch[]>('/shuttlecocks').then((r) => setBatches(r.data))
  }

  useEffect(() => { load() }, [])

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    try {
      await api.post('/shuttlecocks', {
        purchase_date: purchaseDate,
        total_price: parseFloat(totalPrice),
        tube_count: parseInt(tubeCount),
      })
      setPurchaseDate(''); setTotalPrice(''); setTubeCount('')
      load()
    } catch {
      setError('Failed to add batch')
    }
  }

  async function handleDelete(b: Batch) {
    if (b.consumed > 0) {
      alert(`Cannot delete batch ${b.purchase_date}: ${b.consumed} tube(s) already consumed.`)
      return
    }
    if (!confirm(`Delete batch from ${b.purchase_date}?`)) return
    await api.delete(`/shuttlecocks/${b.purchase_date}`)
    load()
  }

  return (
    <div>
      <h2>Shuttlecock inventory</h2>

      <form onSubmit={handleAdd} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <input type="date" value={purchaseDate} onChange={(e) => setPurchaseDate(e.target.value)} required style={inputStyle} />
        <input type="number" min="1" step="1" placeholder="Tubes" value={tubeCount} onChange={(e) => setTubeCount(e.target.value)} required style={{ ...inputStyle, width: 120 }} />
        <input type="number" min="0" step="0.01" placeholder="Total price (€)" value={totalPrice} onChange={(e) => setTotalPrice(e.target.value)} required style={{ ...inputStyle, width: 160 }} />
        <button type="submit" style={btnStyle}>Add batch</button>
      </form>
      {error && <p style={{ color: '#ef4444' }}>{error}</p>}

      <table style={tableStyle}>
        <thead>
          <tr>{['Purchase date', 'Tubes', 'Total €', '€/tube', 'Consumed', 'Remaining', ''].map((h) => <th key={h} style={thStyle}>{h}</th>)}</tr>
        </thead>
        <tbody>
          {batches.map((b) => (
            <tr key={b.id}>
              <td style={tdStyle}>{b.purchase_date}</td>
              <td style={tdStyle}>{b.tube_count}</td>
              <td style={tdStyle}>€{b.total_price.toFixed(2)}</td>
              <td style={tdStyle}>€{b.price_each.toFixed(2)}</td>
              <td style={tdStyle}>{b.consumed}</td>
              <td style={tdStyle}>{b.remaining}</td>
              <td style={tdStyle}>
                <button
                  onClick={() => handleDelete(b)}
                  style={{ ...btnStyle, background: b.consumed > 0 ? '#cbd5e1' : '#ef4444', cursor: b.consumed > 0 ? 'not-allowed' : 'pointer' }}
                  disabled={b.consumed > 0}
                >
                  Delete
                </button>
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
