import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { api } from '../api'
import MoneyMatrix from '../components/MoneyMatrix'

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
  const [searchParams, setSearchParams] = useSearchParams()

  const [period, setPeriod] = useState<Period | null>(null)
  const [sessions, setSessions] = useState<Session[]>([])
  const [venues, setVenues] = useState<Venue[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [batches, setBatches] = useState<Batch[]>([])
  const [uses, setUses] = useState<ShuttlecockUse[]>([])
  const [report, setReport] = useState<Report | null>(null)
  const [payments, setPayments] = useState<Payment[]>([])

  const [newSessionDate, setNewSessionDate] = useState('')
  const [newSessionVenue, setNewSessionVenue] = useState('')
  const [newSessionSlots, setNewSessionSlots] = useState('')

  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null)
  const [participantsBySession, setParticipantsBySession] = useState<Record<string, Participant[]>>({})
  const [newPlayerTelegramId, setNewPlayerTelegramId] = useState('')
  const [newPlayerAdditional, setNewPlayerAdditional] = useState('0')
  const participants = selectedSessionId ? (participantsBySession[selectedSessionId] ?? []) : []

  const [useBatchId, setUseBatchId] = useState('')
  const [useTubes, setUseTubes] = useState('1')

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

  const loadParticipants = useCallback(async (sessionsList: Session[]) => {
    if (sessionsList.length === 0) { setParticipantsBySession({}); return }
    const results = await Promise.all(
      sessionsList.map((s) =>
        api.get<Participant[]>(`/participants?session_date=${s.date}`).then((r) => [s.id, r.data] as const)
      )
    )
    setParticipantsBySession(Object.fromEntries(results))
  }, [])

  useEffect(() => { loadParticipants(sessions) }, [sessions, loadParticipants])

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

  async function handleUpdateVenue(s: Session, venueId: string) {
    await api.put(`/sessions/${s.date}`, { venue: venueId })
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
    setParticipantsBySession((prev) => ({ ...prev, [s.id]: r.data }))
    loadSessions(); loadReport()
  }

  async function handleRemoveParticipant(id: string) {
    const s = sessions.find((x) => x.id === selectedSessionId)
    if (!s) return
    await api.delete(`/participants/${id}`)
    setParticipantsBySession((prev) => ({
      ...prev,
      [s.id]: (prev[s.id] ?? []).filter((p) => p.id !== id),
    }))
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

  useEffect(() => {
    if (searchParams.get('close') === '1' && period && !period.end_date) {
      openCloseModal()
      const next = new URLSearchParams(searchParams)
      next.delete('close')
      setSearchParams(next, { replace: true })
    }
  }, [searchParams, period, setSearchParams])

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

  if (!period) return (
    <>
      <div className="page-header"><h1>Period</h1></div>
      <div className="card empty-state">Loading…</div>
    </>
  )

  const selectedSession = sessions.find((s) => s.id === selectedSessionId) || null
  const availableBatches = batches.filter((b) => b.remaining > 0)
  const totalMoney = report?.total_period_money ?? 0
  const shuttlecockTotal = uses.reduce((a, u) => a + u.price_each * u.tubes_used, 0)
  const shuttlecockTubes = uses.reduce((a, u) => a + u.tubes_used, 0)

  return (
    <>
      <div className="page-header">
        <button onClick={() => navigate('/periods')} className="btn btn-ghost btn-sm">← Back</button>
        <div>
          <h1 style={{ marginBottom: 2 }}>Period {period.start_date}</h1>
          <span className="page-subtitle">
            {period.end_date ? `Ended ${period.end_date}` : 'Currently open'}
          </span>
        </div>
        <div className="page-header-actions">
          <span className={'pill ' + (closed ? 'pill-closed' : 'pill-open')}>
            {closed ? 'Closed' : 'Open'}
          </span>
          <button onClick={handleDeletePeriod} className="btn btn-danger btn-sm">Delete</button>
        </div>
      </div>

      {/* Sessions */}
      <div className="card">
        <div className="card-header">
          <h3>Sessions</h3>
          <span className="chip">{sessions.length} session{sessions.length === 1 ? '' : 's'}</span>
        </div>

        <form onSubmit={handleAddSession} className="form-row" style={{ marginBottom: 18 }}>
          <div className="field">
            <label className="field-label">Date</label>
            <input type="date" value={newSessionDate} onChange={(e) => setNewSessionDate(e.target.value)} required className="input" />
          </div>
          <div className="field" style={{ minWidth: 200 }}>
            <label className="field-label">Venue</label>
            <select className="select" value={newSessionVenue} onChange={(e) => setNewSessionVenue(e.target.value)}>
              <option value="">— none —</option>
              {venues.map((v) => <option key={v.id} value={v.id}>{v.name} (€{v.price_per_slot}/slot)</option>)}
            </select>
          </div>
          <div className="field" style={{ minWidth: 100 }}>
            <label className="field-label">Slots</label>
            <input type="number" step="0.5" min="0" placeholder="0" value={newSessionSlots} onChange={(e) => setNewSessionSlots(e.target.value)} className="input" />
          </div>
          <button type="submit" className="btn btn-primary">Add session</button>
        </form>

        <div style={{ display: 'flex', gap: 20, alignItems: 'flex-start', flexWrap: 'wrap' }}>
          <div className="table-wrap" style={{ flex: '1 1 460px', minWidth: 0 }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Venue</th>
                  <th className="cell-num">People</th>
                  <th className="cell-num">Slots</th>
                  <th className="cell-num">Money</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {sessions.map((s) => (
                  <tr
                    key={s.id}
                    onClick={() => setSelectedSessionId(s.id === selectedSessionId ? null : s.id)}
                    className={'row-clickable' + (s.id === selectedSessionId ? ' row-selected' : '')}
                  >
                    <td>{s.date}</td>
                    <td onClick={(e) => e.stopPropagation()}>
                      {closed ? (
                        s.venue_name ?? <span className="muted">—</span>
                      ) : (
                        <select
                          value={venues.find((v) => v.name === s.venue_name)?.id ?? ''}
                          onChange={(e) => handleUpdateVenue(s, e.target.value)}
                          className="select"
                          style={{ padding: '5px 28px 5px 10px', fontSize: 13 }}
                        >
                          <option value="">—</option>
                          {venues.map((v) => (
                            <option key={v.id} value={v.id}>{v.name}</option>
                          ))}
                        </select>
                      )}
                    </td>
                    <td className="cell-num">{s.people_count}</td>
                    <td className="cell-num">{s.slots}</td>
                    <td className="cell-num cell-money">€{s.total_money.toFixed(2)}</td>
                    <td className="cell-actions">
                      <button onClick={(e) => { e.stopPropagation(); handleUpdateSlots(s) }} className="btn btn-sm btn-ghost">Slots</button>
                      <button onClick={(e) => { e.stopPropagation(); handleDeleteSession(s) }} className="btn btn-sm btn-danger">Del</button>
                    </td>
                  </tr>
                ))}
                {sessions.length === 0 && (
                  <tr><td colSpan={6} className="muted" style={{ textAlign: 'center', padding: 28 }}>No sessions yet.</td></tr>
                )}
              </tbody>
            </table>
          </div>

          {selectedSession && (
            <div style={{ width: 340, flexShrink: 0 }}>
              <h4 style={{ marginBottom: 10 }}>Participants · {selectedSession.date}</h4>
              <form onSubmit={handleAddParticipant} className="form-row" style={{ marginBottom: 10 }}>
                <select
                  className="select"
                  value={newPlayerTelegramId}
                  onChange={(e) => setNewPlayerTelegramId(e.target.value)}
                  style={{ flex: 1, minWidth: 140 }}
                >
                  <option value="">— add player —</option>
                  {users
                    .filter((u) => !participants.some((p) => p.user_telegram_id === u.telegram_id))
                    .map((u) => <option key={u.telegram_id} value={u.telegram_id}>{userLabel(u)}</option>)}
                </select>
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={newPlayerAdditional}
                  onChange={(e) => setNewPlayerAdditional(e.target.value)}
                  className="input"
                  style={{ width: 64 }}
                  title="Plus-ones"
                />
                <button type="submit" className="btn btn-primary btn-sm" disabled={!newPlayerTelegramId}>Add</button>
              </form>
              <div className="table-wrap">
                <table className="table">
                  <thead>
                    <tr><th>User</th><th className="cell-num">+</th><th></th></tr>
                  </thead>
                  <tbody>
                    {participants.map((p) => (
                      <tr key={p.id}>
                        <td>{p.user_name ?? p.user_telegram_id}</td>
                        <td className="cell-num">{p.additional_participants}</td>
                        <td className="cell-actions">
                          <button onClick={() => handleRemoveParticipant(p.id)} className="btn btn-sm btn-danger">×</button>
                        </td>
                      </tr>
                    ))}
                    {participants.length === 0 && (
                      <tr><td colSpan={3} className="muted" style={{ textAlign: 'center', padding: 20 }}>No participants.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Shuttlecock uses */}
      <div className="card">
        <div className="card-header">
          <h3>Shuttlecocks used</h3>
          <span className="chip">Subtotal €{shuttlecockTotal.toFixed(2)}</span>
        </div>
        <form onSubmit={handleAddUse} className="form-row" style={{ marginBottom: 16 }}>
          <div className="field" style={{ minWidth: 280, flex: 1 }}>
            <label className="field-label">Batch</label>
            <select className="select" value={useBatchId} onChange={(e) => setUseBatchId(e.target.value)}>
              <option value="">— pick batch —</option>
              {availableBatches.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.purchase_date} — €{b.price_each.toFixed(2)}/tube (remaining: {b.remaining})
                </option>
              ))}
            </select>
          </div>
          <div className="field" style={{ minWidth: 90 }}>
            <label className="field-label">Tubes</label>
            <input type="number" min="1" step="1" value={useTubes} onChange={(e) => setUseTubes(e.target.value)} className="input" />
          </div>
          <button type="submit" className="btn btn-primary" disabled={!useBatchId}>Consume</button>
        </form>
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Purchase date</th>
                <th className="cell-num">€/tube</th>
                <th className="cell-num">Tubes used</th>
                <th className="cell-num">Subtotal</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {uses.map((u) => (
                <tr key={u.id}>
                  <td>{u.purchase_date}</td>
                  <td className="cell-num">€{u.price_each.toFixed(2)}</td>
                  <td className="cell-num">{u.tubes_used}</td>
                  <td className="cell-num cell-money">€{(u.price_each * u.tubes_used).toFixed(2)}</td>
                  <td className="cell-actions">
                    <button onClick={() => handleDeleteUse(u)} className="btn btn-sm btn-danger">Remove</button>
                  </td>
                </tr>
              ))}
              {uses.length === 0 && (
                <tr><td colSpan={5} className="muted" style={{ textAlign: 'center', padding: 24 }}>No shuttlecocks recorded.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Money split */}
      <div className="card">
        <div className="card-header">
          <h3>Money split {closed ? '(final)' : '(preview)'}</h3>
          <span className="pill pill-accent">Total €{totalMoney.toFixed(2)}</span>
          {!closed && (
            <div className="card-header-actions">
              <button onClick={openCloseModal} className="btn btn-primary">Close period →</button>
            </div>
          )}
        </div>

        <MoneyMatrix
          sessions={sessions}
          participantsBySession={participantsBySession}
          shuttlecockTotal={shuttlecockTotal}
          shuttlecockTubes={shuttlecockTubes}
          totalPeriodMoney={totalMoney}
          personalReport={report?.personal_period_money}
          payments={closed ? payments : undefined}
          users={users}
          onTogglePaid={(telegramId, hasPaid) => {
            const p = payments.find((x) => x.user_telegram_id === telegramId)
            if (p) handleTogglePaid(p)
            else {
              const endpoint = hasPaid ? '/payments/mark-unpaid' : '/payments/mark-paid'
              api.post(endpoint, { period_start_date: startDate, user_telegram_id: telegramId }).then(loadPayments)
            }
          }}
        />
      </div>

      {closeOpen && (
        <div onClick={() => !submitting && setCloseOpen(false)} className="modal-overlay">
          <div onClick={(e) => e.stopPropagation()} className="modal">
            <h3>Close period {startDate}</h3>
            <p className="muted text-small" style={{ marginBottom: 16 }}>
              This will register <strong>€{totalMoney.toFixed(2)}</strong> across{' '}
              <strong>{report?.personal_period_money.length ?? 0}</strong> player(s),
              set the end date, and open a new period.
            </p>
            <div className="row" style={{ marginBottom: 16 }}>
              <div className="field">
                <label className="field-label">End date</label>
                <input type="date" value={closeEndDate} onChange={(e) => setCloseEndDate(e.target.value)} className="input" />
              </div>
              <div className="field">
                <label className="field-label">New period start</label>
                <input type="date" value={newStartDate} onChange={(e) => setNewStartDate(e.target.value)} className="input" />
              </div>
            </div>
            {modalError && <div className="error-banner">{modalError}</div>}
            <div className="row" style={{ justifyContent: 'flex-end' }}>
              <button onClick={() => setCloseOpen(false)} disabled={submitting} className="btn btn-ghost">Cancel</button>
              <button onClick={handleFinalize} disabled={submitting || !closeEndDate || !newStartDate} className="btn btn-primary">
                {submitting ? 'Sending…' : 'Confirm & send'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
