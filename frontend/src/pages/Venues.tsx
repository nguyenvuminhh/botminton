import { useEffect, useState } from 'react'
import { api } from '../api'

interface Venue {
  id: string
  name: string
  location: string
  price_per_slot: number
}

export default function Venues() {
  const [venues, setVenues] = useState<Venue[]>([])
  const [name, setName] = useState('')
  const [location, setLocation] = useState('')
  const [price, setPrice] = useState('')
  const [error, setError] = useState('')

  function load() {
    api.get<Venue[]>('/venues').then((r) => setVenues(r.data))
  }

  useEffect(() => { load() }, [])

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    try {
      await api.post('/venues', { name, location, price_per_slot: parseFloat(price) })
      setName(''); setLocation(''); setPrice('')
      load()
    } catch {
      setError('Failed to create venue')
    }
  }

  async function handleDelete(venueName: string) {
    if (!confirm(`Delete venue "${venueName}"?`)) return
    await api.delete(`/venues/${encodeURIComponent(venueName)}`)
    load()
  }

  return (
    <div>
      <h2>Venues</h2>
      <form onSubmit={handleAdd} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} required style={inputStyle} />
        <input placeholder="Location" value={location} onChange={(e) => setLocation(e.target.value)} required style={inputStyle} />
        <input placeholder="Price/slot (€)" type="number" step="0.01" value={price} onChange={(e) => setPrice(e.target.value)} required style={{ ...inputStyle, width: 140 }} />
        <button type="submit" style={btnStyle}>Add Venue</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <table style={tableStyle}>
        <thead>
          <tr>{['Name', 'Location', 'Price/slot', ''].map((h) => <th key={h} style={thStyle}>{h}</th>)}</tr>
        </thead>
        <tbody>
          {venues.map((v) => (
            <tr key={v.id}>
              <td style={tdStyle}>{v.name}</td>
              <td style={tdStyle}>{v.location}</td>
              <td style={tdStyle}>€{v.price_per_slot}</td>
              <td style={tdStyle}>
                <button onClick={() => handleDelete(v.name)} style={{ ...btnStyle, background: '#ef4444' }}>Delete</button>
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
