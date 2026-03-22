// pages/Listings.jsx — marketplace grid

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getProperties } from '../services/api'
import { Spinner, ErrorBanner, Tag } from '../components/UI'
import { SlidersHorizontal } from 'lucide-react'

export default function Listings() {
  const [properties, setProperties] = useState([])
  const [filtered,   setFiltered]   = useState([])
  const [loading,    setLoading]    = useState(true)
  const [error,      setError]      = useState('')
  const [filters,    setFilters]    = useState({ locality: '', bhk: '', maxRent: '' })
  const navigate = useNavigate()

  useEffect(() => {
    getProperties()
      .then(({ data }) => { setProperties(data); setFiltered(data) })
      .catch(() => setError('Could not load listings. Is the backend running?'))
      .finally(() => setLoading(false))
  }, [])

  // Apply filters
  useEffect(() => {
    let out = [...properties]
    if (filters.locality) out = out.filter(p => p.locality === filters.locality)
    if (filters.bhk)      out = out.filter(p => p.bhk === Number(filters.bhk))
    if (filters.maxRent)  out = out.filter(p => p.rent <= Number(filters.maxRent))
    setFiltered(out)
  }, [filters, properties])

  const setF = (k, v) => setFilters(f => ({ ...f, [k]: v }))

  const localities = [...new Set(properties.map(p => p.locality))].sort()

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">

      {/* Header */}
      <div className="mb-8 fade-up">
        <p className="text-xs font-mono uppercase tracking-widest mb-2" style={{ color: 'var(--accent)' }}>
          Marketplace
        </p>
        <h1 className="font-display font-bold text-3xl">All Listings</h1>
        <p className="mt-2 text-sm" style={{ color: 'var(--muted)' }}>
          {filtered.length} properties available · click any card to see AI analysis
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-8 fade-up-2 items-center">
        <SlidersHorizontal size={15} style={{ color: 'var(--muted)' }} />

        <select value={filters.locality} onChange={e => setF('locality', e.target.value)}
                className="px-3 py-2 rounded-xl text-sm outline-none"
                style={{ background: 'var(--surface)', border: '1px solid var(--border)', color: filters.locality ? 'var(--text)' : 'var(--muted)' }}>
          <option value="">All Localities</option>
          {localities.map(l => <option key={l} value={l}>{l}</option>)}
        </select>

        <select value={filters.bhk} onChange={e => setF('bhk', e.target.value)}
                className="px-3 py-2 rounded-xl text-sm outline-none"
                style={{ background: 'var(--surface)', border: '1px solid var(--border)', color: filters.bhk ? 'var(--text)' : 'var(--muted)' }}>
          <option value="">Any BHK</option>
          {[1,2,3,4].map(n => <option key={n} value={n}>{n} BHK</option>)}
        </select>

        <input type="number" placeholder="Max rent (₹)" value={filters.maxRent}
               onChange={e => setF('maxRent', e.target.value)}
               className="px-3 py-2 rounded-xl text-sm outline-none w-36"
               style={{ background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text)' }} />

        {(filters.locality || filters.bhk || filters.maxRent) && (
          <button onClick={() => setFilters({ locality: '', bhk: '', maxRent: '' })}
                  className="px-3 py-2 rounded-xl text-xs"
                  style={{ color: 'var(--danger)', border: '1px solid rgba(248,113,113,0.3)', background: 'rgba(248,113,113,0.05)' }}>
            Clear filters
          </button>
        )}
      </div>

      {/* States */}
      {loading && (
        <div className="flex justify-center py-20">
          <Spinner size={28} />
        </div>
      )}

      <ErrorBanner message={error} />

      {!loading && !error && filtered.length === 0 && (
        <div className="text-center py-20" style={{ color: 'var(--muted)' }}>
          <div className="text-4xl mb-3">🏘</div>
          <p>No properties found. Try adjusting filters or add one as a landlord.</p>
        </div>
      )}

      {/* Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((p, i) => (
          <PropertyCard key={p.id} property={p} delay={i * 50}
                        onClick={() => navigate(`/property/${p.id}`)} />
        ))}
      </div>
    </div>
  )
}

// Detect if a value is a dummy placeholder left from /docs testing
const isDummy = v => !v || v === 'string' || v === 'number' || v === ''

function PropertyCard({ property: p, onClick, delay }) {
  const hasDummy = isDummy(p.locality) || isDummy(p.furnishing) || isDummy(p.water_source)

  // Quick client-side pricing signal (rough heuristic shown on card)
  // Real verdict comes from /analyze — this is just a teaser
  const priceSignal = null // we don't have predicted rent on the card — show nothing, just CTA

  return (
    <button onClick={onClick} className="text-left rounded-2xl p-5 transition-all duration-250 group"
            style={{
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              animation: `fadeUp 0.4s ${delay}ms ease forwards`,
              opacity: 0,
            }}
            onMouseEnter={e => {
              e.currentTarget.style.borderColor = 'var(--accent)'
              e.currentTarget.style.transform = 'translateY(-2px)'
            }}
            onMouseLeave={e => {
              e.currentTarget.style.borderColor = 'var(--border)'
              e.currentTarget.style.transform = 'translateY(0)'
            }}>

      {/* Dummy data warning */}
      {hasDummy && (
        <div className="mb-3 px-2.5 py-1.5 rounded-lg text-xs"
             style={{ background: 'rgba(251,191,36,0.08)', border: '1px solid rgba(251,191,36,0.25)', color: '#fbbf24' }}>
          ⚠ Test entry — incomplete data
        </div>
      )}

      {/* Top row */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="font-display font-semibold text-base">
            {isDummy(p.locality) ? <span style={{ color: 'var(--muted)' }}>Unknown area</span> : p.locality}
          </p>
          <p className="text-xs mt-0.5" style={{ color: 'var(--muted)' }}>
            {p.bhk} BHK · {p.sqft} sqft
          </p>
        </div>
        <span className="font-mono font-semibold text-sm" style={{ color: 'var(--accent)' }}>
          ₹{p.rent.toLocaleString('en-IN')}
        </span>
      </div>

      {/* Details row */}
      <div className="flex flex-wrap gap-1.5 mb-4">
        {!isDummy(p.furnishing)   && <Tag>{p.furnishing}</Tag>}
        {!isDummy(p.water_source) && <Tag>{p.water_source} water</Tag>}
        <Tag>{p.age}yr old</Tag>
      </div>

      {/* Amenity tags */}
      <div className="flex gap-1.5">
        {p.bachelor_friendly && <Tag color="green">Bachelor ✓</Tag>}
        {p.pet_friendly       && <Tag color="green">Pets ✓</Tag>}
      </div>

      {/* CTA — this is the USP, make it loud */}
      <div className="mt-4 pt-4 flex items-center justify-between"
           style={{ borderTop: '1px solid var(--border)' }}>
        <span className="text-xs" style={{ color: 'var(--muted)' }}>ID #{p.id}</span>
        <span className="px-3 py-1.5 rounded-lg text-xs font-semibold"
              style={{ background: 'rgba(110,231,183,0.1)', color: 'var(--accent)', border: '1px solid rgba(110,231,183,0.2)' }}>
          🧠 Check if overpriced →
        </span>
      </div>
    </button>
  )
}