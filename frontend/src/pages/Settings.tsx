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
  const [venues, setVenues] = useState<Venue[]>([])
  const [venueId, setVenueId] = useState('')
  const [location, setLocation] = useState('')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [dayIndex, setDayIndex] = useState('')
  const [status, setStatus] = useState('')

  const [newVenueName, setNewVenueName] = useState('')
  const [newVenueLocation, setNewVenueLocation] = useState('')
  const [newVenuePrice, setNewVenuePrice] = useState('')
  const [venueError, setVenueError] = useState('')

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
    <>
      <div className="page-header">
        <h1>Settings</h1>
        <span className="page-subtitle">Defaults, venues, and players.</span>
      </div>

      <div className="card">
        <div className="card-header"><h3>Session defaults</h3></div>
        <form onSubmit={handleSaveDefaults} className="stack" style={{ maxWidth: 480 }}>
          <div className="field">
            <label className="field-label">Default venue</label>
            <select className="select" value={venueId} onChange={(e) => setVenueId(e.target.value)}>
              <option value="">— none —</option>
              {venues.map((v) => <option key={v.id} value={v.id}>{v.name} — {v.location}</option>)}
            </select>
          </div>
          <div className="field">
            <label className="field-label">Default location</label>
            <input className="input" value={location} onChange={(e) => setLocation(e.target.value)} />
          </div>
          <div className="row">
            <div className="field">
              <label className="field-label">Start time</label>
              <input type="time" className="input" value={startTime} onChange={(e) => setStartTime(e.target.value)} />
            </div>
            <div className="field">
              <label className="field-label">End time</label>
              <input type="time" className="input" value={endTime} onChange={(e) => setEndTime(e.target.value)} />
            </div>
          </div>
          <div className="field">
            <label className="field-label">Default day of week</label>
            <select className="select" value={dayIndex} onChange={(e) => setDayIndex(e.target.value)}>
              <option value="">— none —</option>
              {DAYS.map((d, i) => <option key={i} value={i}>{d}</option>)}
            </select>
          </div>
          <div className="row">
            <button type="submit" className="btn btn-primary">Save defaults</button>
            {status && <span className={'status-msg ' + (status === 'Saved ✓' ? 'ok' : '')}>{status}</span>}
          </div>
        </form>
      </div>

      <div className="card">
        <div className="card-header"><h3>Venues</h3></div>
        <form onSubmit={handleAddVenue} className="form-row" style={{ marginBottom: 16 }}>
          <div className="field">
            <label className="field-label">Name</label>
            <input className="input" placeholder="e.g. Unisport" value={newVenueName} onChange={(e) => setNewVenueName(e.target.value)} required />
          </div>
          <div className="field">
            <label className="field-label">Location</label>
            <input className="input" placeholder="Address" value={newVenueLocation} onChange={(e) => setNewVenueLocation(e.target.value)} required />
          </div>
          <div className="field" style={{ minWidth: 110 }}>
            <label className="field-label">€/slot</label>
            <input className="input" type="number" step="0.01" min="0" placeholder="10.00" value={newVenuePrice} onChange={(e) => setNewVenuePrice(e.target.value)} required />
          </div>
          <button type="submit" className="btn btn-primary">Add venue</button>
        </form>
        {venueError && <div className="error-banner">{venueError}</div>}

        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Location</th>
                <th className="cell-num">€/slot</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {venues.map((v) => (
                <tr key={v.id}>
                  <td><strong>{v.name}</strong></td>
                  <td className="muted">{v.location}</td>
                  <td className="cell-num cell-money">€{v.price_per_slot}</td>
                  <td className="cell-actions">
                    <button onClick={() => handleDeleteVenue(v.name)} className="btn btn-sm btn-danger">Delete</button>
                  </td>
                </tr>
              ))}
              {venues.length === 0 && (
                <tr><td colSpan={4} className="muted" style={{ textAlign: 'center', padding: 24 }}>No venues yet.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card">
        <div className="card-header"><h3>Players</h3></div>
        <p className="card-hint">Players register automatically when they interact with the Telegram bot.</p>
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Telegram ID</th>
                <th>Username</th>
                <th>Full name</th>
                <th>Admin</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td className="muted" style={{ fontFamily: 'var(--mono)', fontSize: 13 }}>{u.telegram_id}</td>
                  <td>{u.telegram_user_name ? '@' + u.telegram_user_name : <span className="muted">—</span>}</td>
                  <td>{u.full_name ?? <span className="muted">—</span>}</td>
                  <td>
                    <label className="checkbox-row">
                      <input type="checkbox" checked={u.is_admin} onChange={() => handleToggleAdmin(u)} />
                      <span className={u.is_admin ? 'pill pill-accent' : 'muted text-small'}>
                        {u.is_admin ? 'Admin' : '—'}
                      </span>
                    </label>
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr><td colSpan={4} className="muted" style={{ textAlign: 'center', padding: 24 }}>No players yet.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  )
}
