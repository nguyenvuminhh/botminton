import { useEffect, useState } from 'react'
import { api } from '../api'

interface Period { id: string; start_date: string }
interface Session {
  id: string
  date: string
  period_start_date: string | null
  venue_name: string | null
  slots: number
  is_poll_open: boolean
}
interface Participant {
  id: string
  user_telegram_id: string
  user_name: string | null
  additional_participants: number
}

export default function Sessions() {
  const [periods, setPeriods] = useState<Period[]>([])
  const [selectedPeriod, setSelectedPeriod] = useState('')
  const [sessions, setSessions] = useState<Session[]>([])
  const [selectedSession, setSelectedSession] = useState<Session | null>(null)
  const [participants, setParticipants] = useState<Participant[]>([])

  // new session form
  const [newDate, setNewDate] = useState('')
  const [newVenue, setNewVenue] = useState('')
  const [newSlots, setNewSlots] = useState('')

  useEffect(() => {
    api.get<Period[]>('/periods').then((r) => setPeriods(r.data))
  }, [])

  useEffect(() => {
    if (!selectedPeriod) { setSessions([]); return }
    api.get<Session[]>(`/sessions?period=${selectedPeriod}`).then((r) => setSessions(r.data))
  }, [selectedPeriod])

  useEffect(() => {
    if (!selectedSession) { setParticipants([]); return }
    api.get<Participant[]>(`/participants?session_date=${selectedSession.date}`).then((r) => setParticipants(r.data))
  }, [selectedSession])

  async function handleAddSession(e: React.FormEvent) {
    e.preventDefault()
    await api.post('/sessions', { date: newDate, period_id: selectedPeriod, venue_id: newVenue || undefined, slots: parseFloat(newSlots) || 0 })
    setNewDate(''); setNewVenue(''); setNewSlots('')
    api.get<Session[]>(`/sessions?period=${selectedPeriod}`).then((r) => setSessions(r.data))
  }

  async function handleUpdateSlots(s: Session) {
    const slots = prompt('Slots:', String(s.slots))
    if (slots === null) return
    await api.put(`/sessions/${s.date}`, { slots: parseFloat(slots) })
    api.get<Session[]>(`/sessions?period=${selectedPeriod}`).then((r) => setSessions(r.data))
  }

  async function handleDeleteSession(date: string) {
    if (!confirm(`Delete session ${date}?`)) return
    await api.delete(`/sessions/${date}`)
    setSessions((prev) => prev.filter((s) => s.date !== date))
    if (selectedSession?.date === date) setSelectedSession(null)
  }

  async function handleRemoveParticipant(id: string) {
    await api.delete(`/participants/${id}`)
    setParticipants((prev) => prev.filter((p) => p.id !== id))
  }

  return (
    <div>
      <h2>Sessions</h2>
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', alignItems: 'center' }}>
        <label style={{ fontSize: 14 }}>Period:
          <select value={selectedPeriod} onChange={(e) => setSelectedPeriod(e.target.value)} style={inputStyle}>
            <option value="">— select —</option>
            {periods.map((p) => (
              <option key={p.id} value={p.start_date}>{p.start_date}</option>
            ))}
          </select>
        </label>
      </div>

      {selectedPeriod && (
        <form onSubmit={handleAddSession} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
          <input type="date" placeholder="Date" value={newDate} onChange={(e) => setNewDate(e.target.value)} required style={inputStyle} />
          <input placeholder="Venue name" value={newVenue} onChange={(e) => setNewVenue(e.target.value)} style={inputStyle} />
          <input type="number" step="0.5" placeholder="Slots" value={newSlots} onChange={(e) => setNewSlots(e.target.value)} style={{ ...inputStyle, width: 90 }} />
          <button type="submit" style={btnStyle}>Add Session</button>
        </form>
      )}

      <div style={{ display: 'flex', gap: '1.5rem' }}>
        <table style={{ ...tableStyle, flex: 1 }}>
          <thead>
            <tr>{['Date', 'Venue', 'Slots', 'Poll', ''].map((h) => <th key={h} style={thStyle}>{h}</th>)}</tr>
          </thead>
          <tbody>
            {sessions.map((s) => (
              <tr
                key={s.id}
                onClick={() => setSelectedSession(s)}
                style={{ cursor: 'pointer', background: selectedSession?.id === s.id ? '#eff6ff' : undefined }}
              >
                <td style={tdStyle}>{s.date}</td>
                <td style={tdStyle}>{s.venue_name ?? '—'}</td>
                <td style={tdStyle}>{s.slots}</td>
                <td style={tdStyle}>{s.is_poll_open ? '🟢 open' : '⚫ closed'}</td>
                <td style={{ ...tdStyle, display: 'flex', gap: '0.3rem' }}>
                  <button onClick={(e) => { e.stopPropagation(); handleUpdateSlots(s) }} style={btnStyle}>Slots</button>
                  <button onClick={(e) => { e.stopPropagation(); handleDeleteSession(s.date) }} style={{ ...btnStyle, background: '#ef4444' }}>Del</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {selectedSession && (
          <div style={{ width: 300 }}>
            <h4 style={{ marginBottom: '0.5rem' }}>Participants — {selectedSession.date}</h4>
            <table style={tableStyle}>
              <thead>
                <tr>{['User', '+', ''].map((h) => <th key={h} style={thStyle}>{h}</th>)}</tr>
              </thead>
              <tbody>
                {participants.map((p) => (
                  <tr key={p.id}>
                    <td style={tdStyle}>{p.user_name ?? p.user_telegram_id}</td>
                    <td style={tdStyle}>{p.additional_participants}</td>
                    <td style={tdStyle}>
                      <button onClick={() => handleRemoveParticipant(p.id)} style={{ ...btnStyle, background: '#ef4444', padding: '0.2rem 0.5rem' }}>×</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

const inputStyle: React.CSSProperties = { padding: '0.4rem 0.6rem', borderRadius: 4, border: '1px solid #cbd5e1', fontSize: 14 }
const btnStyle: React.CSSProperties = { padding: '0.4rem 0.8rem', borderRadius: 4, border: 'none', background: '#3b82f6', color: '#fff', cursor: 'pointer', fontSize: 14 }
const tableStyle: React.CSSProperties = { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }
const thStyle: React.CSSProperties = { textAlign: 'left', padding: '0.75rem 1rem', background: '#f1f5f9', fontSize: 13, color: '#475569' }
const tdStyle: React.CSSProperties = { padding: '0.6rem 1rem', borderTop: '1px solid #f1f5f9', fontSize: 14 }
