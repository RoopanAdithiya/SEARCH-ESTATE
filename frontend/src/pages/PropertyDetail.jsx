// pages/PropertyDetail.jsx — THE wow moment

import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { analyzeProperty } from '../services/api'
import { Card, Spinner, ErrorBanner, Tag, StatCard } from '../components/UI'
import { ArrowLeft } from 'lucide-react'
import {
  RadialBarChart, RadialBar, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, Cell
} from 'recharts'

export default function PropertyDetail() {
  const { id }  = useParams()
  const navigate = useNavigate()
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')

  useEffect(() => {
    analyzeProperty(id)
      .then(({ data }) => setData(data))
      .catch(e => setError(
        e.response?.status === 404
          ? `Property #${id} not found.`
          : 'Could not load analysis. Is the backend running?'
      ))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="text-center">
        <Spinner size={32} />
        <p className="mt-4 text-sm" style={{ color: 'var(--muted)' }}>Running AI analysis...</p>
      </div>
    </div>
  )

  if (error) return (
    <div className="max-w-2xl mx-auto px-6 py-10">
      <button onClick={() => navigate('/listings')}
              className="flex items-center gap-2 text-sm mb-6"
              style={{ color: 'var(--muted)' }}>
        <ArrowLeft size={14} /> Back to listings
      </button>
      <ErrorBanner message={error} />
    </div>
  )

  const { property: p, analysis: a } = data

  const isOverpriced = a.overpricing?.is_overpriced
  const isGoodDeal   = a.overpricing?.label === 'good deal'

  const barData = [
    { name: 'Predicted', value: a.predicted_rent,         fill: '#6ee7b7' },
    { name: 'Listed',    value: a.overpricing?.listed_rent || 0, fill: isOverpriced ? '#f87171' : '#818cf8' },
  ]

  // Stress gauge data
  const stressData = a.rent_stress ? [
    { name: 'stress', value: a.rent_stress.rent_to_income, fill:
        a.rent_stress.label === 'comfortable' ? '#6ee7b7'
      : a.rent_stress.label === 'moderate'    ? '#fbbf24' : '#f87171'
    }
  ] : []

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">

      {/* Back */}
      <button onClick={() => navigate('/listings')}
              className="flex items-center gap-2 text-sm mb-8 transition-colors fade-up"
              style={{ color: 'var(--muted)' }}
              onMouseEnter={e => e.currentTarget.style.color = 'var(--text)'}
              onMouseLeave={e => e.currentTarget.style.color = 'var(--muted)'}>
        <ArrowLeft size={14} /> Back to listings
      </button>

      {/* Header */}
      <div className="mb-8 fade-up-2">
        <div className="flex items-center gap-3 flex-wrap">
          <h1 className="font-display font-bold text-3xl">{p.locality}</h1>
          {isOverpriced && <Tag color="red">⚠ Overpriced</Tag>}
          {isGoodDeal   && <Tag color="green">✓ Good Deal</Tag>}
          {!isOverpriced && !isGoodDeal && a.overpricing && <Tag color="yellow">≈ Fair Price</Tag>}
        </div>
        <p className="mt-2 text-sm" style={{ color: 'var(--muted)' }}>
          Property #{p.id} · {p.bhk} BHK · {p.sqft} sqft · {p.furnishing} furnished
        </p>
      </div>

      {/* Split layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* LEFT — Property Info */}
        <div className="flex flex-col gap-4 fade-up-2">
          <Card>
            <p className="text-xs uppercase tracking-widest mb-4" style={{ color: 'var(--muted)' }}>
              Property Details
            </p>
            <div className="grid grid-cols-2 gap-3">
              <StatCard icon="📍" label="Locality"  value={p.locality} />
              <StatCard icon="📐" label="Area"      value={`${p.sqft} sqft`} sub={`${p.bhk} BHK`} />
              <StatCard icon="🛋" label="Furnished" value={p.furnishing} />
              <StatCard icon="💧" label="Water"     value={p.water_source} />
              <StatCard icon="🏗" label="Age"       value={`${p.age} years`} />
              <StatCard icon="💰" label="Listed Rent" accent
                        value={`₹${p.listed_rent.toLocaleString('en-IN')}`} />
            </div>
          </Card>

          {/* Tags */}
          <Card>
            <p className="text-xs uppercase tracking-widest mb-3" style={{ color: 'var(--muted)' }}>
              Amenities
            </p>
            <div className="flex gap-2 flex-wrap">
              <Tag color={p.bachelor_friendly ? 'green' : 'default'}>
                {p.bachelor_friendly ? '✓' : '✗'} Bachelor Friendly
              </Tag>
              <Tag color={p.pet_friendly ? 'green' : 'default'}>
                {p.pet_friendly ? '✓' : '✗'} Pet Friendly
              </Tag>
            </div>
          </Card>
        </div>

        {/* RIGHT — AI Analysis */}
        <div className="flex flex-col gap-4 fade-up-3">

          {/* Verdict banner */}
          <div className="rounded-2xl px-5 py-4"
               style={{
                 background: isOverpriced ? 'rgba(248,113,113,0.06)' : 'rgba(110,231,183,0.06)',
                 border: `1px solid ${isOverpriced ? 'rgba(248,113,113,0.25)' : 'rgba(110,231,183,0.25)'}`,
               }}>
            <p className="text-xs uppercase tracking-widest mb-1"
               style={{ color: isOverpriced ? 'var(--danger)' : 'var(--accent)' }}>
              AI Verdict
            </p>
            <p className="text-sm font-medium">{a.verdict}</p>
          </div>

          {/* Key numbers */}
          <div className="grid grid-cols-2 gap-3">
            <StatCard icon="🧠" label="Predicted Fair Rent" accent
                      value={`₹${a.predicted_rent.toLocaleString('en-IN')}`} />
            {a.overpricing && (
              <StatCard
                icon={isOverpriced ? '⚠️' : '✅'}
                label="vs Market"
                value={`${a.overpricing.difference_pct > 0 ? '+' : ''}${a.overpricing.difference_pct}%`}
                sub={a.overpricing.label}
              />
            )}
          </div>

          {/* Bar chart — predicted vs listed */}
          <Card>
            <p className="text-xs uppercase tracking-widest mb-4" style={{ color: 'var(--muted)' }}>
              Predicted vs Listed Rent
            </p>
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={barData} barSize={50}>
                <XAxis dataKey="name" tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false}
                       tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} />
                <Tooltip
                  formatter={v => [`₹${v.toLocaleString('en-IN')}`, '']}
                  contentStyle={{ background: '#1a1a24', border: '1px solid #2a2a3a', borderRadius: 10, fontSize: 12, color: '#f0f0f5' }}
                  labelStyle={{ color: '#6b7280' }}
                  itemStyle={{ color: '#f0f0f5' }}
                  cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                />
                <Bar dataKey="value" radius={[6,6,0,0]}>
                  {barData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
          {/* SHAP Explanation */}
          {a.explanation?.length > 0 && (
            <Card className="fade-up-4">
              <p className="text-xs uppercase tracking-widest mb-4" style={{ color: 'var(--muted)' }}>
                Why this price?
              </p>
              <div className="flex flex-col gap-3">
                {a.explanation.map((item, i) => {
                  const isPositive = item.impact > 0
                  const barWidth   = Math.min(100, Math.round((Math.abs(item.impact) / a.predicted_rent) * 100 * 3))
                  const color      = isPositive ? '#6ee7b7' : '#f87171'
                  return (
                    <div key={i} className="flex flex-col gap-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-sm">{item.feature}</span>
                        <span className="font-mono text-sm font-semibold" style={{ color }}>
                          {isPositive ? '+' : ''}₹{Math.abs(item.impact).toLocaleString('en-IN')}
                        </span>
                      </div>
                      <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--surface2)' }}>
                        <div className="h-full rounded-full transition-all duration-500"
                             style={{ width: `${barWidth}%`, background: color, opacity: 0.7 }} />
                      </div>
                    </div>
                  )
                })}
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}