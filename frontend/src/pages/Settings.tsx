import { useEffect, useState } from 'react'
import { api } from '../api'

interface Venue {
  id: string
  name: string
  location: string
  price_per_slot: number
}

interface Metadata {
  default_venue_id: string | null
  default_location: string | null
  default_start_time: string | null
  default_end_time: string | null
  default_day_of_the_week_index: number | null
}

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

export default function Settings() {
  const [venues, setVenues] = useState<Venue[]>([])
  const [venueId, setVenueId] = useState('')
  const [location, setLocation] = useState('')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [dayIndex, setDayIndex] = useState('')
  const [status, setStatus] = useState<string>('')

  useEffect(() => {
    api.get<Venue[]>('/venues').then((r) => setVenues(r.data))
    api.get<Metadata>('/metadata').then((r) => {
      setVenueId(r.data.default_venue_id ?? '')
      setLocation(r.data.default_location ?? '')
      setStartTime(r.data.default_start_time ?? '')
      setEndTime(r.data.default_end_time ?? '')
      setDayIndex(r.data.default_day_of_the_week_index !== null && r.data.default_day_of_the_week_index !== undefined
        ? String(r.data.default_day_of_the_week_index)
        : '')
    })
  }, [])

  async function handleSave(e: React.FormEvent) {
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

  return (
    <div>
      <h2>Settings — Session Defaults</h2>
      <p style={{ color: '#64748b', fontSize: 14, marginBottom: '1rem' }}>
        These defaults are used when new sessions are scheduled (via the bot or the web).
      </p>

      <form onSubmit={handleSave} style={{ maxWidth: 480, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <label style={labelStyle}>
          Default venue
          <select value={venueId} onChange={(e) => setVenueId(e.target.value)} style={inputStyle}>
            <option value="">— none —</option>
            {venues.map((v) => (
              <option key={v.id} value={v.id}>{v.name} — {v.location}</option>
            ))}
          </select>
        </label>

        <label style={labelStyle}>
          Default location
          <input value={location} onChange={(e) => setLocation(e.target.value)} style={inputStyle} />
        </label>

        <label style={labelStyle}>
          Default start time
          <input type="time" value={startTime} onChange={(e) => setStartTime(e.target.value)} style={inputStyle} />
        </label>

        <label style={labelStyle}>
          Default end time
          <input type="time" value={endTime} onChange={(e) => setEndTime(e.target.value)} style={inputStyle} />
        </label>

        <label style={labelStyle}>
          Default day of week
          <select value={dayIndex} onChange={(e) => setDayIndex(e.target.value)} style={inputStyle}>
            <option value="">— none —</option>
            {DAYS.map((d, i) => (
              <option key={i} value={i}>{d}</option>
            ))}
          </select>
        </label>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <button type="submit" style={btnStyle}>Save</button>
          {status && <span style={{ fontSize: 14, color: '#64748b' }}>{status}</span>}
        </div>
      </form>
    </div>
  )
}

const labelStyle: React.CSSProperties = { display: 'flex', flexDirection: 'column', gap: '0.25rem', fontSize: 14, color: '#334155' }
const inputStyle: React.CSSProperties = { padding: '0.4rem 0.6rem', borderRadius: 4, border: '1px solid #cbd5e1', fontSize: 14 }
const btnStyle: React.CSSProperties = { padding: '0.5rem 1rem', borderRadius: 4, border: 'none', background: '#3b82f6', color: '#fff', cursor: 'pointer', fontSize: 14 }
