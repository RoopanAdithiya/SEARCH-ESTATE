// pages/Listings.jsx — map left, cards right

import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import { getProperties } from '../services/api'
import { Spinner, ErrorBanner, Tag } from '../components/UI'
import { SlidersHorizontal } from 'lucide-react'
import 'leaflet/dist/leaflet.css'

const LOCALITY_COORDS = {
  'Velachery':      [12.9815, 80.2180],
  'Anna Nagar':     [13.0850, 80.2101],
  'Adyar':          [13.0012, 80.2565],
  'T Nagar':        [13.0418, 80.2341],
  'Porur':          [13.0368, 80.1573],
  'Chromepet':      [12.9516, 80.1462],
  'Sholinganallur': [12.9010, 80.2279],
  'Perambur':       [13.1143, 80.2329],
  'Korattur':       [13.1103, 80.1863],
  'Medavakkam':     [12.9255, 80.1982],
  'Tambaram':       [12.9249, 80.1000],
  'Mylapore':       [13.0368, 80.2676],
  'Nungambakkam':   [13.0569, 80.2425],
  'Kodambakkam':    [13.0524, 80.2270],
  'OMR':            [12.9121, 80.2275],
}

function getMarkerColor(property, allProperties) {
  const sameArea = allProperties.filter(p => p.locality === property.locality)
  if (sameArea.length < 2) return '#6ee7b7'
  const avg = sameArea.reduce((s, p) => s + p.rent, 0) / sameArea.length
  const ratio = property.rent / avg
  if (ratio > 1.25) return '#f87171'
  if (ratio < 0.85) return '#818cf8'
  return '#6ee7b7'
}

function MapFlyTo({ coords }) {
  const map = useMap()
  useEffect(() => {
    if (coords) map.flyTo(coords, 14, { duration: 0.8 })
  }, [coords, map])
  return null
}

const isDummy = v => !v || v === 'string' || v === 'number' || v === ''

export default function Listings() {
  const [properties, setProperties] = useState([])
  const [filtered,   setFiltered]   = useState([])
  const [loading,    setLoading]    = useState(true)
  const [error,      setError]      = useState('')
  const [filters,    setFilters]    = useState({ locality: '', bhk: '', maxRent: '' })
  const [hoveredId,  setHoveredId]  = useState(null)
  const [flyTarget,  setFlyTarget]  = useState(null)
  const cardRefs                    = useRef({})
  const navigate                    = useNavigate()

  useEffect(() => {
    getProperties()
      .then(({ data }) => { setProperties(data); setFiltered(data) })
      .catch(() => setError('Could not load listings. Is the backend running?'))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    let out = [...properties]
    if (filters.locality) out = out.filter(p => p.locality === filters.locality)
    if (filters.bhk)      out = out.filter(p => p.bhk === Number(filters.bhk))
    if (filters.maxRent)  out = out.filter(p => p.rent <= Number(filters.maxRent))
    setFiltered(out)
  }, [filters, properties])

  const setF = (k, v) => setFilters(f => ({ ...f, [k]: v }))
  const localities = [...new Set(properties.map(p => p.locality))].sort()

  const handleMarkerClick = (id) => {
    setHoveredId(id)
    const el = cardRefs.current[id]
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }

  const handleCardHover = (property) => {
    setHoveredId(property.id)
    if (property.lat && property.lng) setFlyTarget([property.lat, property.lng])
  }

  return (
    <div style={{ height: 'calc(100vh - 57px)', display: 'flex', flexDirection: 'column' }}>

      {/* Header bar */}
      <div className="px-6 py-4 flex-shrink-0"
           style={{ borderBottom: '1px solid var(--border)' }}>
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <p className="text-xs font-mono uppercase tracking-widest mb-0.5" style={{ color: 'var(--accent)' }}>Marketplace</p>
            <h1 className="font-display font-bold text-xl">
              All Listings
              <span className="ml-2 text-sm font-normal" style={{ color: 'var(--muted)' }}>{filtered.length} properties</span>
            </h1>
          </div>
          <div className="flex flex-wrap gap-2 items-center">
            <SlidersHorizontal size={14} style={{ color: 'var(--muted)' }} />
            <select value={filters.locality} onChange={e => setF('locality', e.target.value)}
                    className="px-3 py-2 rounded-xl text-xs outline-none"
                    style={{ background: 'var(--surface2)', border: '1px solid var(--border)', color: filters.locality ? 'var(--text)' : 'var(--muted)' }}>
              <option value="">All Localities</option>
              {localities.map(l => <option key={l} value={l}>{l}</option>)}
            </select>
            <select value={filters.bhk} onChange={e => setF('bhk', e.target.value)}
                    className="px-3 py-2 rounded-xl text-xs outline-none"
                    style={{ background: 'var(--surface2)', border: '1px solid var(--border)', color: filters.bhk ? 'var(--text)' : 'var(--muted)' }}>
              <option value="">Any BHK</option>
              {[1,2,3,4].map(n => <option key={n} value={n}>{n} BHK</option>)}
            </select>
            <input type="number" placeholder="Max rent (₹)" value={filters.maxRent}
                   onChange={e => setF('maxRent', e.target.value)}
                   className="px-3 py-2 rounded-xl text-xs outline-none w-32"
                   style={{ background: 'var(--surface2)', border: '1px solid var(--border)', color: 'var(--text)' }} />
            {(filters.locality || filters.bhk || filters.maxRent) && (
              <button onClick={() => setFilters({ locality: '', bhk: '', maxRent: '' })}
                      className="px-3 py-2 rounded-xl text-xs"
                      style={{ color: 'var(--danger)', border: '1px solid rgba(248,113,113,0.3)', background: 'rgba(248,113,113,0.05)' }}>
                Clear
              </button>
            )}
          </div>
        </div>
        <div className="flex items-center gap-4 mt-3 text-xs" style={{ color: 'var(--muted)' }}>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full inline-block" style={{ background: '#6ee7b7' }} />Fair price</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full inline-block" style={{ background: '#f87171' }} />Likely overpriced</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full inline-block" style={{ background: '#818cf8' }} />Possible deal</span>
        </div>
      </div>

      {/* Split */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>

        {/* LEFT — Map */}
        <div style={{ width: '55%', position: 'relative', flexShrink: 0 }}>
          <MapContainer center={[13.0067, 80.2206]} zoom={12}
                        style={{ height: '100%', width: '100%' }}>
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
              attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            />
            {flyTarget && <MapFlyTo coords={flyTarget} />}
            {filtered.map(p => {
              if (!p.lat || !p.lng || isDummy(p.locality)) return null
              const coords = [p.lat, p.lng]
              const color     = getMarkerColor(p, properties)
              const isHovered = hoveredId === p.id
              return (
                <CircleMarker key={p.id} center={coords}
                              radius={isHovered ? 14 : 10}
                              pathOptions={{
                                fillColor: color, fillOpacity: isHovered ? 1 : 0.75,
                                color: isHovered ? '#fff' : color, weight: isHovered ? 2 : 1,
                              }}
                              eventHandlers={{ click: () => handleMarkerClick(p.id) }}>
                  <Popup>
                    <div style={{ background: '#1a1a24', border: '1px solid #2a2a3a', borderRadius: 10, padding: '10px 14px', minWidth: 160, fontFamily: 'DM Sans, sans-serif' }}>
                      <div style={{ fontWeight: 700, fontSize: 14, color: '#f0f0f5', marginBottom: 4 }}>{p.locality}</div>
                      <div style={{ fontSize: 12, color: '#6b7280', marginBottom: 6 }}>{p.bhk} BHK · {p.sqft} sqft</div>
                      <div style={{ fontSize: 16, fontWeight: 700, color, marginBottom: 8 }}>₹{p.rent.toLocaleString('en-IN')}</div>
                      <button onClick={() => navigate(`/property/${p.id}`)}
                              style={{ background: 'rgba(110,231,183,0.15)', color: '#6ee7b7', border: '1px solid rgba(110,231,183,0.3)', borderRadius: 8, padding: '4px 10px', fontSize: 11, cursor: 'pointer', fontWeight: 600, width: '100%' }}>
                        🧠 AI Analysis →
                      </button>
                    </div>
                  </Popup>
                </CircleMarker>
              )
            })}
          </MapContainer>
        </div>

        {/* RIGHT — Cards */}
        <div style={{ width: '45%', overflowY: 'auto', padding: '16px', background: 'var(--bg)' }}>
          {loading && <div className="flex justify-center py-20"><Spinner size={28} /></div>}
          <ErrorBanner message={error} />
          {!loading && !error && filtered.length === 0 && (
            <div className="text-center py-20" style={{ color: 'var(--muted)' }}>
              <div className="text-4xl mb-3">🏘</div>
              <p className="text-sm">No properties found. Try adjusting filters.</p>
            </div>
          )}
          <div className="flex flex-col gap-3">
            {filtered.map((p, i) => (
              <div key={p.id} ref={el => cardRefs.current[p.id] = el}>
                <PropertyCard property={p} isHighlighted={hoveredId === p.id}
                              delay={i * 40}
                              onHover={() => handleCardHover(p)}
                              onLeave={() => setHoveredId(null)}
                              onClick={() => navigate(`/property/${p.id}`)}
                              allProperties={properties} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function PropertyCard({ property: p, onClick, onHover, onLeave, isHighlighted, delay, allProperties }) {
  const hasDummy    = isDummy(p.locality) || isDummy(p.furnishing) || isDummy(p.water_source)
  const markerColor = getMarkerColor(p, allProperties)

  return (
    <button onClick={onClick} onMouseEnter={onHover} onMouseLeave={onLeave}
            className="w-full text-left rounded-2xl p-4 transition-all duration-200"
            style={{
              background: isHighlighted ? 'var(--surface2)' : 'var(--surface)',
              border: `1px solid ${isHighlighted ? 'var(--accent)' : 'var(--border)'}`,
              animation: `fadeUp 0.35s ${delay}ms ease forwards`,
              opacity: 0,
              transform: isHighlighted ? 'translateX(2px)' : 'none',
            }}>
      {hasDummy && (
        <div className="mb-2 px-2 py-1 rounded-lg text-xs"
             style={{ background: 'rgba(251,191,36,0.08)', border: '1px solid rgba(251,191,36,0.2)', color: '#fbbf24' }}>
          ⚠ Test entry
        </div>
      )}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: markerColor }} />
            <p className="font-display font-semibold text-sm truncate">
              {isDummy(p.locality) ? <span style={{ color: 'var(--muted)' }}>Unknown</span> : p.locality}
            </p>
          </div>
          <p className="text-xs mb-2" style={{ color: 'var(--muted)' }}>
            {p.bhk} BHK · {p.sqft} sqft · {p.age}yr old
          </p>
          <div className="flex flex-wrap gap-1">
            {!isDummy(p.furnishing)   && <Tag>{p.furnishing}</Tag>}
            {!isDummy(p.water_source) && <Tag>{p.water_source}</Tag>}
            {p.bachelor_friendly && <Tag color="green">Bachelor ✓</Tag>}
            {p.pet_friendly      && <Tag color="green">Pets ✓</Tag>}
          </div>
        </div>
        <div className="flex flex-col items-end gap-2 flex-shrink-0">
          <span className="font-mono font-bold text-base" style={{ color: 'var(--accent)' }}>
            ₹{p.rent.toLocaleString('en-IN')}
          </span>
          <span className="px-2.5 py-1 rounded-lg text-xs font-semibold"
                style={{ background: 'rgba(110,231,183,0.1)', color: 'var(--accent)', border: '1px solid rgba(110,231,183,0.2)' }}>
            🧠 Analyze →
          </span>
        </div>
      </div>
    </button>
  )
}