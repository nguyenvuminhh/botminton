import { useEffect, useState } from 'react'
import { api } from '../api'

interface Venue { id: string; name: string; location: string; price_per_slot: number }
interface Metadata {
  default_venue_id: string | null
  default_location: string | null
  default_start_time: string | null
  default_end_time: string | null
  default_day_of_the_week_index: number | null
}
interface User {
  id: string
  telegram_id: string
  telegram_user_name: string | null
  full_name: string | null
  is_admin: boolean
}

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

export default function Settings() {
  // Defaults
  const [venues, setVenues] = useState<Venue[]>([])
  const [venueId, setVenueId] = useState('')
  const [location, setLocation] = useState('')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [dayIndex, setDayIndex] = useState('')
  const [status, setStatus] = useState('')

  // Venue form
  const [newVenueName, setNewVenueName] = useState('')
  const [newVenueLocation, setNewVenueLocation] = useState('')
  const [newVenuePrice, setNewVenuePrice] = useState('')
  const [venueError, setVenueError] = useState('')

  // Players
  const [users, setUsers] = useState<User[]>([])

  function loadVenues() {
    api.get<Venue[]>('/venues').then((r) => setVenues(r.data))
  }
  function loadUsers() {
    api.get<User[]>('/users').then((r) => setUsers(r.data))
  }

  useEffect(() => {
    loadVenues()
    loadUsers()
    api.get<Metadata>('/metadata').then((r) => {
      setVenueId(r.data.default_venue_id ?? '')
      setLocation(r.data.default_location ?? '')
      setStartTime(r.data.default_start_time ?? '')
      setEndTime(r.data.default_end_time ?? '')
      setDayIndex(
        r.data.default_day_of_the_week_index !== null && r.data.default_day_of_the_week_index !== undefined
          ? String(r.data.default_day_of_the_week_index) : ''
      )
    })
  }, [])

  async function handleSaveDefaults(e: React.FormEvent) {
    e.preventDefault()
    setStatus('Saving…')
    try {
      await api.put('/metadata', {
        default_venue_id: venueId || null,
        default_location: location || null,
        default_start_time: startTime || null,
        default_end_time: endTime || null,
        default_day_of_the_week_index: dayIndex !== '' ? parseInt(dayIndex) : null,
      })
      setStatus('Saved ✓')
    } catch {
      setStatus('Save failed')
    }
  }

  async function handleAddVenue(e: React.FormEvent) {
    e.preventDefault()
    setVenueError('')
    try {
      await api.post('/venues', {
        name: newVenueName,
        location: newVenueLocation,
        price_per_slot: parseFloat(newVenuePrice),
      })
      setNewVenueName(''); setNewVenueLocation(''); setNewVenuePrice('')
      loadVenues()
    } catch {
      setVenueError('Failed to add venue')
    }
  }

  async function handleDeleteVenue(name: string) {
    if (!confirm(`Delete venue "${name}"?`)) return
    await api.delete(`/venues/${name}`)
    loadVenues()
  }

  async function handleToggleAdmin(u: User) {
    await api.put(`/users/${u.telegram_id}`, { is_admin: !u.is_admin })
    loadUsers()
  }

  return (
    <div>
      <h2>Settings</h2>

      {/* Defaults */}
      <section style={sectionStyle}>
        <h3 style={h3Style}>Session defaults</h3>
        <form onSubmit={handleSaveDefaults} style={{ maxWidth: 480, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <label style={labelStyle}>Default venue
            <select value={venueId} onChange={(e) => setVenueId(e.target.value)} style={inputStyle}>
              <option value="">— none —</option>
              {venues.map((v) => <option key={v.id} value={v.id}>{v.name} — {v.location}</option>)}
            </select>
          </label>
          <label style={labelStyle}>Default location
            <input value={location} onChange={(e) => setLocation(e.target.value)} style={inputStyle} />
          </label>
          <label style={labelStyle}>Default start time
            <input type="time" value={startTime} onChange={(e) => setStartTime(e.target.value)} style={inputStyle} />
          </label>
          <label style={labelStyle}>Default end time
            <input type="time" value={endTime} onChange={(e) => setEndTime(e.target.value)} style={inputStyle} />
          </label>
          <label style={labelStyle}>Default day of week
            <select value={dayIndex} onChange={(e) => setDayIndex(e.target.value)} style={inputStyle}>
              <option value="">— none —</option>
              {DAYS.map((d, i) => <option key={i} value={i}>{d}</option>)}
            </select>
          </label>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <button type="submit" style={btnStyle}>Save</button>
            {status && <span style={{ fontSize: 14, color: '#64748b' }}>{status}</span>}
          </div>
        </form>
      </section>

      {/* Venues */}
      <section style={sectionStyle}>
        <h3 style={h3Style}>Venues</h3>
        <form onSubmit={handleAddVenue} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
          <input placeholder="Name" value={newVenueName} onChange={(e) => setNewVenueName(e.target.value)} required style={inputStyle} />
          <input placeholder="Location" value={newVenueLocation} onChange={(e) => setNewVenueLocation(e.target.value)} required style={inputStyle} />
          <input type="number" step="0.01" min="0" placeholder="€/slot" value={newVenuePrice} onChange={(e) => setNewVenuePrice(e.target.value)} required style={{ ...inputStyle, width: 110 }} />
          <button type="submit" style={btnStyle}>Add venue</button>
        </form>
        {venueError && <p style={{ color: '#ef4444' }}>{venueError}</p>}
        <table style={tableStyle}>
          <thead>
            <tr>{['Name', 'Location', '€/slot', ''].map((h) => <th key={h} style={thStyle}>{h}</th>)}</tr>
          </thead>
          <tbody>
            {venues.map((v) => (
              <tr key={v.id}>
                <td style={tdStyle}>{v.name}</td>
                <td style={tdStyle}>{v.location}</td>
                <td style={tdStyle}>€{v.price_per_slot}</td>
                <td style={tdStyle}>
                  <button onClick={() => handleDeleteVenue(v.name)} style={{ ...btnStyle, background: '#ef4444' }}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* Players */}
      <section style={sectionStyle}>
        <h3 style={h3Style}>Players</h3>
        <p style={{ color: '#64748b', fontSize: 14 }}>
          Players are registered automatically when they interact with the Telegram bot.
        </p>
        <table style={tableStyle}>
          <thead>
            <tr>{['Telegram ID', 'Username', 'Full name', 'Admin'].map((h) => <th key={h} style={thStyle}>{h}</th>)}</tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td style={tdStyle}>{u.telegram_id}</td>
                <td style={tdStyle}>{u.telegram_user_name ?? '—'}</td>
                <td style={tdStyle}>{u.full_name ?? '—'}</td>
                <td style={tdStyle}>
                  <label style={{ cursor: 'pointer' }}>
                    <input type="checkbox" checked={u.is_admin} onChange={() => handleToggleAdmin(u)} />
                    <span style={{ marginLeft: 6 }}>{u.is_admin ? 'Admin' : '—'}</span>
                  </label>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}

const sectionStyle: React.CSSProperties = { background: '#fff', borderRadius: 8, padding: '1.25rem', marginBottom: '1.5rem', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }
const h3Style: React.CSSProperties = { marginTop: 0, marginBottom: '1rem', fontSize: 16 }
const labelStyle: React.CSSProperties = { display: 'flex', flexDirection: 'column', gap: '0.25rem', fontSize: 14, color: '#334155' }
const inputStyle: React.CSSProperties = { padding: '0.4rem 0.6rem', borderRadius: 4, border: '1px solid #cbd5e1', fontSize: 14 }
const btnStyle: React.CSSProperties = { padding: '0.5rem 1rem', borderRadius: 4, border: 'none', background: '#3b82f6', color: '#fff', cursor: 'pointer', fontSize: 14 }
const tableStyle: React.CSSProperties = { width: '100%', borderCollapse: 'collapse', background: '#fff' }
const thStyle: React.CSSProperties = { textAlign: 'left', padding: '0.6rem 0.8rem', background: '#f1f5f9', fontSize: 13, color: '#475569' }
const tdStyle: React.CSSProperties = { padding: '0.5rem 0.8rem', borderTop: '1px solid #f1f5f9', fontSize: 14 }
