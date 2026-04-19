import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'

interface Period { id: string; start_date: string; end_date: string | null; total_money: number | null }
interface Session {
  id: string
  date: string
  venue_name: string | null
  slots: number
  people_count: number
  total_money: number
  is_poll_open: boolean
}
interface Venue { id: string; name: string; location: string; price_per_slot: number }
interface Participant {
  id: string
  user_telegram_id: string
  user_name: string | null
  additional_participants: number
}
interface User { id: string; telegram_id: string; telegram_user_name: string | null; full_name: string | null }
interface Batch {
  id: string
  purchase_date: string
  tube_count: number
  price_each: number
  remaining: number
}
interface ShuttlecockUse {
  id: string
  batch_id: string
  purchase_date: string
  price_each: number
  tubes_used: number
}
interface ReportEntry { person_id: string; telegram_user_name: string; full_name: string | null; period_money: number }
interface Report { period_start_date: string; period_end_date: string; total_period_money: number; personal_period_money: ReportEntry[] }
interface Payment {
  id: string
  user_telegram_id: string
  user_name: string | null
  amount: number
  has_paid: boolean
  period_start_date: string | null
}

function todayISO() { return new Date().toISOString().split('T')[0] }
function tomorrowISO() {
  const d = new Date(); d.setDate(d.getDate() + 1)
  return d.toISOString().split('T')[0]
}

export default function PeriodDetail() {
  const { startDate = '' } = useParams<{ startDate: string }>()
  const navigate = useNavigate()

  const [period, setPeriod] = useState<Period | null>(null)
  const [sessions, setSessions] = useState<Session[]>([])
  const [venues, setVenues] = useState<Venue[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [batches, setBatches] = useState<Batch[]>([])
  const [uses, setUses] = useState<ShuttlecockUse[]>([])
  const [report, setReport] = useState<Report | null>(null)
  const [payments, setPayments] = useState<Payment[]>([])

  // Session add form
  const [newSessionDate, setNewSessionDate] = useState('')
  const [newSessionVenue, setNewSessionVenue] = useState('')
  const [newSessionSlots, setNewSessionSlots] = useState('')

  // Selected session + participants panel
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null)
  const [participants, setParticipants] = useState<Participant[]>([])
  const [newPlayerTelegramId, setNewPlayerTelegramId] = useState('')
  const [newPlayerAdditional, setNewPlayerAdditional] = useState('0')

  // Shuttlecock use form
  const [useBatchId, setUseBatchId] = useState('')
  const [useTubes, setUseTubes] = useState('1')

  // Close-period modal
  const [closeOpen, setCloseOpen] = useState(false)
  const [closeEndDate, setCloseEndDate] = useState('')
  const [newStartDate, setNewStartDate] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [modalError, setModalError] = useState('')

  const closed = Boolean(period?.end_date)

  const loadPeriod = useCallback(() => {
    api.get<Period>(`/periods/${startDate}`).then((r) => setPeriod(r.data)).catch(() => setPeriod(null))
  }, [startDate])
  const loadSessions = useCallback(() => {
    api.get<Session[]>(`/sessions?period=${startDate}`).then((r) => setSessions(r.data))
  }, [startDate])
  const loadUses = useCallback(() => {
    api.get<ShuttlecockUse[]>(`/periods/${startDate}/shuttlecocks`).then((r) => setUses(r.data))
  }, [startDate])
  const loadReport = useCallback(() => {
    api.get<Report>(`/payments/report/${startDate}`).then((r) => setReport(r.data)).catch(() => setReport(null))
  }, [startDate])
  const loadPayments = useCallback(() => {
    api.get<Payment[]>(`/payments?period=${startDate}`).then((r) => setPayments(r.data)).catch(() => setPayments([]))
  }, [startDate])

  useEffect(() => {
    loadPeriod()
    loadSessions()
    loadUses()
    loadReport()
    loadPayments()
    api.get<Venue[]>('/venues').then((r) => setVenues(r.data))
    api.get<User[]>('/users').then((r) => setUsers(r.data))
    api.get<Batch[]>('/shuttlecocks').then((r) => setBatches(r.data))
  }, [startDate, loadPeriod, loadSessions, loadUses, loadReport, loadPayments])

  useEffect(() => {
    if (!selectedSessionId) { setParticipants([]); return }
    const s = sessions.find((x) => x.id === selectedSessionId)
    if (!s) return
    api.get<Participant[]>(`/participants?session_date=${s.date}`).then((r) => setParticipants(r.data))
  }, [selectedSessionId, sessions])

  async function handleAddSession(e: React.FormEvent) {
    e.preventDefault()
    if (!period) return
    await api.post('/sessions', {
      date: newSessionDate,
      period_id: period.id,
      venue_id: newSessionVenue || undefined,
      slots: parseFloat(newSessionSlots) || 0,
    })
    setNewSessionDate(''); setNewSessionVenue(''); setNewSessionSlots('')
    loadSessions(); loadReport()
  }

  async function handleUpdateSlots(s: Session) {
    const v = prompt('Slots:', String(s.slots))
    if (v === null) return
    await api.put(`/sessions/${s.date}`, { slots: parseFloat(v) })
    loadSessions(); loadReport()
  }

  async function handleDeleteSession(s: Session) {
    if (!confirm(`Delete session ${s.date}?`)) return
    await api.delete(`/sessions/${s.date}`)
    if (selectedSessionId === s.id) setSelectedSessionId(null)
    loadSessions(); loadReport()
  }

  async function handleAddParticipant(e: React.FormEvent) {
    e.preventDefault()
    const s = sessions.find((x) => x.id === selectedSessionId)
    if (!s || !newPlayerTelegramId) return
    await api.post('/participants', {
      user_telegram_id: newPlayerTelegramId,
      session_date: s.date,
      additional_participants: parseInt(newPlayerAdditional) || 0,
    })
    setNewPlayerTelegramId(''); setNewPlayerAdditional('0')
    const r = await api.get<Participant[]>(`/participants?session_date=${s.date}`)
    setParticipants(r.data)
    loadSessions(); loadReport()
  }

  async function handleRemoveParticipant(id: string) {
    const s = sessions.find((x) => x.id === selectedSessionId)
    if (!s) return
    await api.delete(`/participants/${id}`)
    setParticipants((prev) => prev.filter((p) => p.id !== id))
    loadSessions(); loadReport()
  }

  async function handleAddUse(e: React.FormEvent) {
    e.preventDefault()
    if (!useBatchId) return
    await api.post(`/periods/${startDate}/shuttlecocks`, {
      batch_id: useBatchId,
      tubes_used: parseInt(useTubes) || 0,
    })
    setUseBatchId(''); setUseTubes('1')
    loadUses(); loadReport()
    api.get<Batch[]>('/shuttlecocks').then((r) => setBatches(r.data))
  }

  async function handleDeleteUse(u: ShuttlecockUse) {
    if (!confirm(`Remove ${u.tubes_used} tube(s) from ${u.purchase_date}?`)) return
    await api.delete(`/periods/${startDate}/shuttlecocks/${u.id}`)
    loadUses(); loadReport()
    api.get<Batch[]>('/shuttlecocks').then((r) => setBatches(r.data))
  }

  async function handleTogglePaid(p: Payment) {
    const endpoint = p.has_paid ? '/payments/mark-unpaid' : '/payments/mark-paid'
    await api.post(endpoint, { period_start_date: startDate, user_telegram_id: p.user_telegram_id })
    loadPayments()
  }

  async function handleDeletePeriod() {
    if (!confirm(`Delete period ${startDate}? This cascades to sessions.`)) return
    await api.delete(`/periods/${startDate}`)
    navigate('/periods')
  }

  function openCloseModal() {
    setCloseEndDate(todayISO())
    setNewStartDate(tomorrowISO())
    setModalError('')
    setCloseOpen(true)
  }

  async function handleFinalize() {
    setSubmitting(true); setModalError('')
    try {
      await api.post(`/periods/${startDate}/finalize`, {
        end_date: closeEndDate,
        new_period_start_date: newStartDate,
      })
      setCloseOpen(false)
      loadPeriod(); loadPayments(); loadReport()
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setModalError(msg || 'Failed to finalize period')
    } finally {
      setSubmitting(false)
    }
  }

  function userLabel(u: User) { return u.full_name || u.telegram_user_name || u.telegram_id }

  if (!period) return <p>Loading…</p>

  const selectedSession = sessions.find((s) => s.id === selectedSessionId) || null
  const availableBatches = batches.filter((b) => b.remaining > 0)
  const totalMoney = report?.total_period_money ?? 0

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
        <button onClick={() => navigate('/periods')} style={{ ...btnStyle, background: '#94a3b8' }}>← Back</button>
        <h2 style={{ margin: 0 }}>
          Period {period.start_date} → {period.end_date ?? <em style={{ color: '#94a3b8' }}>open</em>}
        </h2>
        <span style={{ marginLeft: 'auto', color: '#64748b' }}>{closed ? 'Closed' : 'Open'}</span>
        <button onClick={handleDeletePeriod} style={{ ...btnStyle, background: '#ef4444' }}>Delete period</button>
      </div>

      {/* Sessions section */}
      <section style={sectionStyle}>
        <h3 style={h3Style}>Sessions</h3>
        <form onSubmit={handleAddSession} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
          <input type="date" value={newSessionDate} onChange={(e) => setNewSessionDate(e.target.value)} required style={inputStyle} />
          <select value={newSessionVenue} onChange={(e) => setNewSessionVenue(e.target.value)} style={inputStyle}>
            <option value="">— venue —</option>
            {venues.map((v) => <option key={v.id} value={v.id}>{v.name} (€{v.price_per_slot}/slot)</option>)}
          </select>
          <input type="number" step="0.5" min="0" placeholder="Slots" value={newSessionSlots} onChange={(e) => setNewSessionSlots(e.target.value)} style={{ ...inputStyle, width: 90 }} />
          <button type="submit" style={btnStyle}>Add session</button>
        </form>

        <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'flex-start' }}>
          <table style={{ ...tableStyle, flex: 1 }}>
            <thead>
              <tr>{['Date', 'Venue', 'People', 'Slots', 'Money', ''].map((h) => <th key={h} style={thStyle}>{h}</th>)}</tr>
            </thead>
            <tbody>
              {sessions.map((s) => (
                <tr
                  key={s.id}
                  onClick={() => setSelectedSessionId(s.id === selectedSessionId ? null : s.id)}
                  style={{ cursor: 'pointer', background: s.id === selectedSessionId ? '#eff6ff' : undefined }}
                >
                  <td style={tdStyle}>{s.date}</td>
                  <td style={tdStyle}>{s.venue_name ?? '—'}</td>
                  <td style={tdStyle}>{s.people_count}</td>
                  <td style={tdStyle}>{s.slots}</td>
                  <td style={tdStyle}>€{s.total_money.toFixed(2)}</td>
                  <td style={{ ...tdStyle, display: 'flex', gap: '0.3rem' }}>
                    <button onClick={(e) => { e.stopPropagation(); handleUpdateSlots(s) }} style={btnStyle}>Slots</button>
                    <button onClick={(e) => { e.stopPropagation(); handleDeleteSession(s) }} style={{ ...btnStyle, background: '#ef4444' }}>Del</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {selectedSession && (
            <div style={{ width: 320 }}>
              <h4 style={{ marginBottom: '0.5rem' }}>Participants — {selectedSession.date}</h4>
              <form onSubmit={handleAddParticipant} style={{ display: 'flex', gap: '0.3rem', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
                <select value={newPlayerTelegramId} onChange={(e) => setNewPlayerTelegramId(e.target.value)} style={{ ...inputStyle, flex: 1, minWidth: 140 }}>
                  <option value="">— add player —</option>
                  {users
                    .filter((u) => !participants.some((p) => p.user_telegram_id === u.telegram_id))
                    .map((u) => <option key={u.telegram_id} value={u.telegram_id}>{userLabel(u)}</option>)}
                </select>
                <input type="number" min="0" step="1" value={newPlayerAdditional} onChange={(e) => setNewPlayerAdditional(e.target.value)} style={{ ...inputStyle, width: 60 }} title="Plus-ones" />
                <button type="submit" style={btnStyle} disabled={!newPlayerTelegramId}>Add</button>
              </form>
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
      </section>

      {/* Shuttlecock uses */}
      <section style={sectionStyle}>
        <h3 style={h3Style}>Shuttlecocks used in this period</h3>
        <form onSubmit={handleAddUse} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
          <select value={useBatchId} onChange={(e) => setUseBatchId(e.target.value)} style={{ ...inputStyle, minWidth: 280 }}>
            <option value="">— pick batch —</option>
            {availableBatches.map((b) => (
              <option key={b.id} value={b.id}>
                {b.purchase_date} — €{b.price_each.toFixed(2)}/tube (remaining: {b.remaining})
              </option>
            ))}
          </select>
          <input type="number" min="1" step="1" value={useTubes} onChange={(e) => setUseTubes(e.target.value)} style={{ ...inputStyle, width: 80 }} />
          <button type="submit" style={btnStyle} disabled={!useBatchId}>Consume</button>
        </form>
        <table style={tableStyle}>
          <thead>
            <tr>{['Purchase date', '€/tube', 'Tubes used', 'Subtotal', ''].map((h) => <th key={h} style={thStyle}>{h}</th>)}</tr>
          </thead>
          <tbody>
            {uses.map((u) => (
              <tr key={u.id}>
                <td style={tdStyle}>{u.purchase_date}</td>
                <td style={tdStyle}>€{u.price_each.toFixed(2)}</td>
                <td style={tdStyle}>{u.tubes_used}</td>
                <td style={tdStyle}>€{(u.price_each * u.tubes_used).toFixed(2)}</td>
                <td style={tdStyle}>
                  <button onClick={() => handleDeleteUse(u)} style={{ ...btnStyle, background: '#ef4444' }}>Remove</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* Money split preview */}
      <section style={sectionStyle}>
        <h3 style={h3Style}>
          Money split {closed ? '(final)' : '(preview)'} — Total: €{totalMoney.toFixed(2)}
        </h3>

        {closed ? (
          <table style={tableStyle}>
            <thead>
              <tr>{['Player', 'Amount', 'Paid'].map((h) => <th key={h} style={thStyle}>{h}</th>)}</tr>
            </thead>
            <tbody>
              {payments.map((p) => (
                <tr key={p.id}>
                  <td style={tdStyle}>{p.user_name ?? p.user_telegram_id}</td>
                  <td style={tdStyle}>€{p.amount.toFixed(2)}</td>
                  <td style={tdStyle}>
                    <label style={{ cursor: 'pointer' }}>
                      <input type="checkbox" checked={p.has_paid} onChange={() => handleTogglePaid(p)} />
                      <span style={{ marginLeft: 6, color: p.has_paid ? '#22c55e' : '#64748b' }}>
                        {p.has_paid ? 'Paid' : 'Unpaid'}
                      </span>
                    </label>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <>
            <table style={tableStyle}>
              <thead>
                <tr>{['Player', 'Amount'].map((h) => <th key={h} style={thStyle}>{h}</th>)}</tr>
              </thead>
              <tbody>
                {(report?.personal_period_money ?? []).map((e) => (
                  <tr key={e.person_id}>
                    <td style={tdStyle}>{e.full_name || e.telegram_user_name}</td>
                    <td style={tdStyle}>€{e.period_money.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
              <button onClick={openCloseModal} style={btnStyle}>Close period</button>
            </div>
          </>
        )}
      </section>

      {closeOpen && (
        <div onClick={() => !submitting && setCloseOpen(false)} style={overlayStyle}>
          <div onClick={(e) => e.stopPropagation()} style={modalStyle}>
            <h3 style={{ marginTop: 0 }}>Close period {startDate}</h3>
            <p style={{ color: '#64748b', fontSize: 14 }}>
              This will register €{totalMoney.toFixed(2)} across {report?.personal_period_money.length ?? 0} player(s),
              set the end date, and open a new period.
            </p>
            <div style={{ display: 'flex', gap: '1rem', margin: '1rem 0', flexWrap: 'wrap' }}>
              <label style={{ fontSize: 13, color: '#475569' }}>End date
                <input type="date" value={closeEndDate} onChange={(e) => setCloseEndDate(e.target.value)} style={inputStyle} />
              </label>
              <label style={{ fontSize: 13, color: '#475569' }}>New period start
                <input type="date" value={newStartDate} onChange={(e) => setNewStartDate(e.target.value)} style={inputStyle} />
              </label>
            </div>
            {modalError && <p style={{ color: '#ef4444', fontSize: 14 }}>{modalError}</p>}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
              <button onClick={() => setCloseOpen(false)} disabled={submitting} style={{ ...btnStyle, background: '#94a3b8' }}>Cancel</button>
              <button onClick={handleFinalize} disabled={submitting || !closeEndDate || !newStartDate} style={btnStyle}>
                {submitting ? 'Sending…' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

const sectionStyle: React.CSSProperties = { background: '#fff', borderRadius: 8, padding: '1.25rem', marginBottom: '1.5rem', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }
const h3Style: React.CSSProperties = { marginTop: 0, marginBottom: '1rem', fontSize: 16 }
const inputStyle: React.CSSProperties = { display: 'block', marginTop: 4, padding: '0.4rem 0.6rem', borderRadius: 4, border: '1px solid #cbd5e1', fontSize: 14 }
const btnStyle: React.CSSProperties = { padding: '0.4rem 0.8rem', borderRadius: 4, border: 'none', background: '#3b82f6', color: '#fff', cursor: 'pointer', fontSize: 14 }
const tableStyle: React.CSSProperties = { width: '100%', borderCollapse: 'collapse', background: '#fff' }
const thStyle: React.CSSProperties = { textAlign: 'left', padding: '0.6rem 0.8rem', background: '#f1f5f9', fontSize: 13, color: '#475569' }
const tdStyle: React.CSSProperties = { padding: '0.5rem 0.8rem', borderTop: '1px solid #f1f5f9', fontSize: 14 }
const overlayStyle: React.CSSProperties = { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }
const modalStyle: React.CSSProperties = { background: '#fff', borderRadius: 8, padding: '1.5rem', width: '100%', maxWidth: 480, boxShadow: '0 8px 24px rgba(0,0,0,0.2)' }
