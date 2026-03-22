// pages/Tenant.jsx — THE hero page

import { useState } from 'react'
import { predictRent } from '../services/api'
import { Card, Input, Select, Button, ErrorBanner, StatCard } from '../components/UI'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from 'recharts'

const LOCALITIES = [
  'Velachery','Anna Nagar','Adyar','T Nagar','Porur',
  'Chromepet','Sholinganallur','Perambur','Korattur',
  'Medavakkam','Tambaram','Mylapore','Nungambakkam','Kodambakkam','OMR'
].map(l => ({ value: l, label: l }))

const initForm = {
  locality: 'Velachery', sqft: '', bhk: '2',
  furnishing: 'semi', water_source: 'metro',
  age: '', income: '',
}

export default function Tenant() {
  const [form,    setForm]    = useState(initForm)
  const [result,  setResult]  = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async () => {
    setError(''); setResult(null)
    if (!form.sqft || !form.age) { setError('Please fill in all fields.'); return }
    setLoading(true)
    try {
      const payload = {
        locality:     form.locality,
        sqft:         Number(form.sqft),
        bhk:          Number(form.bhk),
        furnishing:   form.furnishing,
        water_source: form.water_source,
        age:          Number(form.age),
        ...(form.income && { monthly_income: Number(form.income) }),
      }
      const { data } = await predictRent(payload)
      setResult(data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Something went wrong. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  // Chart data
  const chartData = result ? [
    { name: 'Predicted', value: result.predicted_rent, fill: '#6ee7b7' },
    ...(result.overpricing ? [{ name: 'Listed', value: result.overpricing.listed_rent, fill: '#f87171' }] : []),
    ...(result.rent_stress  ? [{ name: 'Your Budget (40%)', value: Math.round(result.rent_stress.monthly_income * 0.4), fill: '#818cf8' }] : []),
  ] : []

  const stressColor = result?.rent_stress?.label === 'comfortable' ? 'green'
                    : result?.rent_stress?.label === 'moderate'    ? 'yellow' : 'red'

  const overpricingColor = !result?.overpricing    ? 'default'
    : result.overpricing.is_overpriced             ? 'red'
    : result.overpricing.label === 'good deal'     ? 'green' : 'yellow'

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">

      {/* Header */}
      <div className="mb-10 fade-up">
        <p className="text-xs font-mono uppercase tracking-widest mb-2" style={{ color: 'var(--accent)' }}>
          Tenant Analysis
        </p>
        <h1 className="font-display font-bold text-3xl">Is this rent fair?</h1>
        <p className="mt-2 text-sm" style={{ color: 'var(--muted)' }}>
          Enter property details and let the AI tell you what it's actually worth.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">

        {/* Form */}
        <Card className="lg:col-span-2 fade-up-2 flex flex-col gap-5">
          <Select label="Locality" value={form.locality}
                  onChange={e => set('locality', e.target.value)}
                  options={LOCALITIES} />
          <div className="grid grid-cols-2 gap-3">
            <Input label="Sqft" type="number" placeholder="1000"
                   value={form.sqft} onChange={e => set('sqft', e.target.value)} />
            <Select label="BHK" value={form.bhk}
                    onChange={e => set('bhk', e.target.value)}
                    options={[1,2,3,4].map(n => ({ value: n, label: `${n} BHK` }))} />
          </div>
          <Select label="Furnishing" value={form.furnishing}
                  onChange={e => set('furnishing', e.target.value)}
                  options={[
                    { value: 'full', label: 'Fully Furnished' },
                    { value: 'semi', label: 'Semi Furnished' },
                    { value: 'unfurnished', label: 'Unfurnished' },
                  ]} />
          <Select label="Water Source" value={form.water_source}
                  onChange={e => set('water_source', e.target.value)}
                  options={[
                    { value: 'metro', label: 'Metro Water' },
                    { value: 'borewell', label: 'Borewell' },
                    { value: 'both', label: 'Both' },
                  ]} />
          <Input label="Building Age (years)" type="number" placeholder="5"
                 value={form.age} onChange={e => set('age', e.target.value)} />
          <Input label="Your Monthly Income (optional)" type="number" placeholder="60000"
                 value={form.income} onChange={e => set('income', e.target.value)} />

          <ErrorBanner message={error} />

          <Button loading={loading} onClick={handleSubmit} className="w-full pulse-glow">
            {loading ? 'Analyzing...' : '→ Analyze Rent'}
          </Button>
        </Card>

        {/* Results */}
        <div className="lg:col-span-3 flex flex-col gap-5">
          {!result && !loading && (
            <div className="flex-1 flex items-center justify-center rounded-2xl fade-up-3"
                 style={{ border: '1px dashed var(--border)', minHeight: 300 }}>
              <div className="text-center">
                <div className="text-4xl mb-3">🧠</div>
                <p className="text-sm" style={{ color: 'var(--muted)' }}>
                  Fill in the details and hit Analyze.<br />The model will do the rest.
                </p>
              </div>
            </div>
          )}

          {result && (
            <>
              {/* Stat cards */}
              <div className="grid grid-cols-2 gap-3 fade-up">
                <StatCard icon="💰" label="Predicted Fair Rent" accent
                          value={`₹${result.predicted_rent.toLocaleString('en-IN')}`}
                          sub="per month" />
                {result.overpricing && (
                  <StatCard
                    icon={result.overpricing.is_overpriced ? '⚠️' : '✅'}
                    label="Overpricing"
                    value={`${result.overpricing.difference_pct > 0 ? '+' : ''}${result.overpricing.difference_pct}%`}
                    sub={result.overpricing.label}
                  />
                )}
                {result.rent_stress && (() => {
                  const s = result.rent_stress
                  const cfg = s.label === 'comfortable'
                    ? { icon: '✅', color: '#6ee7b7', bg: 'rgba(110,231,183,0.08)', border: 'rgba(110,231,183,0.25)', headline: 'Affordable', sub: "You're within a healthy range" }
                    : s.label === 'moderate'
                    ? { icon: '⚠️', color: '#fbbf24', bg: 'rgba(251,191,36,0.08)',  border: 'rgba(251,191,36,0.25)',  headline: 'Moderate Strain', sub: "Manageable but tight" }
                    : { icon: '🔴', color: '#f87171', bg: 'rgba(248,113,113,0.08)', border: 'rgba(248,113,113,0.25)', headline: 'High Stress', sub: "This rent will strain your finances" }
                  return (
                    <div className="rounded-2xl p-5 flex flex-col gap-1.5"
                         style={{ background: cfg.bg, border: `1px solid ${cfg.border}` }}>
                      <div className="text-xl">{cfg.icon}</div>
                      <div className="text-xs uppercase tracking-widest" style={{ color: 'var(--muted)' }}>Rent Stress</div>
                      <div className="text-2xl font-display font-bold" style={{ color: cfg.color }}>{cfg.headline}</div>
                      <div className="text-xs" style={{ color: 'var(--muted)' }}>{s.rent_to_income}% of income · {cfg.sub}</div>
                    </div>
                  )
                })()}
              </div>

              {/* Verdict */}
              {(() => {
                const isOver = result.overpricing?.is_overpriced
                const isGood = result.overpricing?.label === 'good deal'
                const isHighStress = result.rent_stress?.label === 'high stress'
                const color  = isOver || isHighStress ? '#f87171' : isGood ? '#6ee7b7' : '#6ee7b7'
                const bg     = isOver || isHighStress ? 'rgba(248,113,113,0.06)' : 'rgba(110,231,183,0.05)'
                const border = isOver || isHighStress ? 'rgba(248,113,113,0.2)'  : 'rgba(110,231,183,0.2)'
                return (
                  <div className="rounded-2xl px-5 py-4 fade-up-2"
                       style={{ background: bg, border: `1px solid ${border}` }}>
                    <p className="text-xs uppercase tracking-widest mb-1" style={{ color }}>AI Verdict</p>
                    <p className="text-sm font-medium">{result.verdict}</p>
                  </div>
                )
              })()}

              {/* SHAP Explanation */}
              {result.explanation?.length > 0 && (
                <Card className="fade-up-3">
                  <p className="text-xs uppercase tracking-widest mb-4" style={{ color: 'var(--muted)' }}>
                    Why this price?
                  </p>
                  <div className="flex flex-col gap-3">
                    {result.explanation.map((item, i) => (
                      <ShapRow key={i} item={item} predicted={result.predicted_rent} />
                    ))}
                  </div>
                </Card>
              )}

              {/* Chart */}
              {chartData.length > 1 && (
                <Card className="fade-up-3">
                  <div className="flex items-center justify-between mb-4">
                    <p className="text-xs uppercase tracking-widest" style={{ color: 'var(--muted)' }}>
                      Predicted vs Affordable Budget
                    </p>
                    <div className="flex items-center gap-3 text-xs" style={{ color: 'var(--muted)' }}>
                      <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm inline-block" style={{ background: '#6ee7b7' }} /> Fair rent</span>
                      {result.overpricing && <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm inline-block" style={{ background: '#f87171' }} /> Listed</span>}
                      {result.rent_stress && <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm inline-block" style={{ background: '#818cf8' }} /> Your 40% limit</span>}
                    </div>
                  </div>
                  <ResponsiveContainer width="100%" height={180}>
                    <BarChart data={chartData} barSize={40}>
                      <XAxis dataKey="name" tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false}
                             tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} />
                      <Tooltip
                        formatter={v => [`₹${v.toLocaleString('en-IN')}`, '']}
                        contentStyle={{ background: 'var(--surface2)', border: '1px solid var(--border)', borderRadius: 10, fontSize: 12 }}
                        cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                      />
                      <Bar dataKey="value" radius={[6,6,0,0]}>
                        {chartData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </Card>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

// ── SHAP row component ────────────────────────────────────────────────────────
function ShapRow({ item, predicted }) {
  const isPositive = item.impact > 0
  const barWidth   = Math.min(100, Math.round((Math.abs(item.impact) / predicted) * 100 * 3))
  const color      = isPositive ? '#6ee7b7' : '#f87171'
  const sign       = isPositive ? '+' : ''

  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between">
        <span className="text-sm">{item.feature}</span>
        <span className="font-mono text-sm font-semibold" style={{ color }}>
          {sign}₹{Math.abs(item.impact).toLocaleString('en-IN')}
        </span>
      </div>
      <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--surface2)' }}>
        <div className="h-full rounded-full transition-all duration-500"
             style={{ width: `${barWidth}%`, background: color, opacity: 0.7 }} />
      </div>
    </div>
  )
}