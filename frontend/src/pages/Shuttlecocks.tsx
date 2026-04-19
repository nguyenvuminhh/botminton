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

  const totalRemaining = batches.reduce((a, b) => a + b.remaining, 0)
  const totalSpend = batches.reduce((a, b) => a + b.total_price, 0)

  return (
    <>
      <div className="page-header">
        <h1>Shuttlecocks</h1>
        <span className="page-subtitle">{batches.length} batch{batches.length === 1 ? '' : 'es'}</span>
        <div className="page-header-actions">
          <span className="chip">Remaining {totalRemaining} tubes</span>
          <span className="chip">Total €{totalSpend.toFixed(2)}</span>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>New batch</h3>
        </div>
        <form onSubmit={handleAdd} className="form-row">
          <div className="field">
            <label className="field-label">Purchase date</label>
            <input type="date" value={purchaseDate} onChange={(e) => setPurchaseDate(e.target.value)} required className="input" />
          </div>
          <div className="field" style={{ minWidth: 100 }}>
            <label className="field-label">Tubes</label>
            <input type="number" min="1" step="1" placeholder="e.g. 12" value={tubeCount} onChange={(e) => setTubeCount(e.target.value)} required className="input" />
          </div>
          <div className="field" style={{ minWidth: 140 }}>
            <label className="field-label">Total €</label>
            <input type="number" min="0" step="0.01" placeholder="0.00" value={totalPrice} onChange={(e) => setTotalPrice(e.target.value)} required className="input" />
          </div>
          <button type="submit" className="btn btn-primary">Add batch</button>
        </form>
        {error && <div className="error-banner" style={{ marginTop: 14, marginBottom: 0 }}>{error}</div>}
      </div>

      <div className="card" style={{ padding: 0 }}>
        <div className="table-wrap" style={{ border: 'none' }}>
          <table className="table">
            <thead>
              <tr>
                <th>Purchase date</th>
                <th className="cell-num">Tubes</th>
                <th className="cell-num">Total</th>
                <th className="cell-num">€/tube</th>
                <th className="cell-num">Consumed</th>
                <th className="cell-num">Remaining</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {batches.map((b) => (
                <tr key={b.id}>
                  <td>{b.purchase_date}</td>
                  <td className="cell-num">{b.tube_count}</td>
                  <td className="cell-num cell-money">€{b.total_price.toFixed(2)}</td>
                  <td className="cell-num">€{b.price_each.toFixed(2)}</td>
                  <td className="cell-num">{b.consumed}</td>
                  <td className="cell-num">
                    <span className={'pill ' + (b.remaining > 0 ? 'pill-accent' : 'pill-closed')}>
                      {b.remaining}
                    </span>
                  </td>
                  <td className="cell-actions">
                    <button
                      onClick={() => handleDelete(b)}
                      className={'btn btn-sm ' + (b.consumed > 0 ? 'btn-ghost' : 'btn-danger')}
                      disabled={b.consumed > 0}
                      title={b.consumed > 0 ? 'Cannot delete — already consumed' : 'Delete batch'}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {batches.length === 0 && (
                <tr><td colSpan={7} className="muted" style={{ textAlign: 'center', padding: 32 }}>No batches yet.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  )
}
