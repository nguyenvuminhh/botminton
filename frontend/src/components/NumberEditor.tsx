import { useState } from 'react'

export default function NumberEditor({ value, step = 1, label, disabled = false, onSave }: {
  value: number; step?: number; label: string; disabled?: boolean; onSave: (value: number) => Promise<void>
}) {
  const [draft, setDraft] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const text = draft ?? String(value)
  const number = Number(text)
  const valid = text.trim() !== '' && Number.isFinite(number) && number >= 0 && Math.abs(number / step - Math.round(number / step)) < 0.000001

  async function save(next: number) {
    if (disabled || saving) return
    if (next === value) { setDraft(null); return }
    setSaving(true); setError('')
    try { await onSave(next); setDraft(null) }
    catch { setError('Could not save. Try again.') }
    finally { setSaving(false) }
  }

  return (
    <div>
      <div className="number-editor" role="group" aria-label={label}>
        <button type="button" className="btn btn-ghost btn-sm" disabled={disabled || saving || value <= 0} aria-label={`Decrease ${label}`} onClick={() => save(Math.max(0, value - step))}>−</button>
        <input className="input" type="number" min="0" step={step} aria-label={label} value={text} disabled={disabled || saving}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter' && valid) { e.preventDefault(); void save(number) } if (e.key === 'Escape') { setDraft(null); setError('') } }} />
        <button type="button" className="btn btn-ghost btn-sm" disabled={disabled || saving} aria-label={`Increase ${label}`} onClick={() => save(value + step)}>+</button>
        {draft !== null && number !== value && <button type="button" className="btn btn-primary btn-sm" disabled={disabled || !valid || saving} onClick={() => save(number)}>Save</button>}
      </div>
      {error && <span className="status-msg" role="alert">{error}</span>}
    </div>
  )
}
