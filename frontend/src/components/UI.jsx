// components/UI.jsx — reusable bits used across all pages

import { Loader2 } from 'lucide-react'

// ── Spinner ───────────────────────────────────────────────────────────────────
export function Spinner({ size = 20 }) {
  return <Loader2 size={size} className="animate-spin" style={{ color: 'var(--accent)' }} />
}

// ── Card ──────────────────────────────────────────────────────────────────────
export function Card({ children, className = '', style = {} }) {
  return (
    <div className={`rounded-2xl p-6 ${className}`}
         style={{ background: 'var(--surface)', border: '1px solid var(--border)', ...style }}>
      {children}
    </div>
  )
}

// ── Input ─────────────────────────────────────────────────────────────────────
export function Input({ label, ...props }) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label className="text-xs font-medium uppercase tracking-widest"
                        style={{ color: 'var(--muted)' }}>{label}</label>}
      <input {...props}
             className="w-full px-4 py-3 rounded-xl text-sm outline-none transition-all duration-200 font-body"
             style={{
               background: 'var(--surface2)',
               border: '1px solid var(--border)',
               color: 'var(--text)',
             }}
             onFocus={e => e.target.style.borderColor = 'var(--accent)'}
             onBlur={e  => e.target.style.borderColor = 'var(--border)'} />
    </div>
  )
}

// ── Select ────────────────────────────────────────────────────────────────────
export function Select({ label, options, ...props }) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label className="text-xs font-medium uppercase tracking-widest"
                        style={{ color: 'var(--muted)' }}>{label}</label>}
      <select {...props}
              className="w-full px-4 py-3 rounded-xl text-sm outline-none transition-all duration-200"
              style={{
                background: 'var(--surface2)',
                border: '1px solid var(--border)',
                color: 'var(--text)',
              }}
              onFocus={e => e.target.style.borderColor = 'var(--accent)'}
              onBlur={e  => e.target.style.borderColor = 'var(--border)'}>
        {options.map(o => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </div>
  )
}

// ── Button ────────────────────────────────────────────────────────────────────
export function Button({ children, loading, variant = 'primary', ...props }) {
  const base = "px-6 py-3 rounded-xl font-display font-semibold text-sm tracking-wide transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
  const styles = {
    primary: { background: 'var(--accent)', color: '#0a0a0f' },
    ghost:   { background: 'var(--surface2)', color: 'var(--text)', border: '1px solid var(--border)' },
  }
  return (
    <button {...props} disabled={loading || props.disabled} className={base}
            style={styles[variant]}>
      {loading ? <Spinner size={16} /> : children}
    </button>
  )
}

// ── Error banner ──────────────────────────────────────────────────────────────
export function ErrorBanner({ message }) {
  if (!message) return null
  return (
    <div className="px-4 py-3 rounded-xl text-sm"
         style={{ background: 'rgba(248,113,113,0.1)', border: '1px solid var(--danger)', color: 'var(--danger)' }}>
      ⚠ {message}
    </div>
  )
}

// ── Stat card ─────────────────────────────────────────────────────────────────
export function StatCard({ icon, label, value, sub, accent = false }) {
  return (
    <div className="rounded-2xl p-5 flex flex-col gap-2"
         style={{
           background: accent ? 'rgba(110,231,183,0.06)' : 'var(--surface2)',
           border: `1px solid ${accent ? 'rgba(110,231,183,0.3)' : 'var(--border)'}`,
         }}>
      <div className="text-xl">{icon}</div>
      <div className="text-xs uppercase tracking-widest" style={{ color: 'var(--muted)' }}>{label}</div>
      <div className="text-2xl font-display font-bold"
           style={{ color: accent ? 'var(--accent)' : 'var(--text)' }}>{value}</div>
      {sub && <div className="text-xs" style={{ color: 'var(--muted)' }}>{sub}</div>}
    </div>
  )
}

// ── Tag ───────────────────────────────────────────────────────────────────────
export function Tag({ children, color = 'default' }) {
  const colors = {
    default: { background: 'var(--surface2)', color: 'var(--muted)', border: 'var(--border)' },
    green:   { background: 'rgba(110,231,183,0.1)', color: 'var(--accent)', border: 'rgba(110,231,183,0.3)' },
    red:     { background: 'rgba(248,113,113,0.1)', color: 'var(--danger)', border: 'rgba(248,113,113,0.3)' },
    yellow:  { background: 'rgba(251,191,36,0.1)',  color: 'var(--warning)', border: 'rgba(251,191,36,0.3)' },
  }
  const c = colors[color]
  return (
    <span className="px-2.5 py-1 rounded-lg text-xs font-medium"
          style={{ background: c.background, color: c.color, border: `1px solid ${c.border}` }}>
      {children}
    </span>
  )
}