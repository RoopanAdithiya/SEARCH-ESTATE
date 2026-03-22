// pages/Landlord.jsx

import { useState } from 'react'
import { addProperty } from '../services/api'
import { Card, Input, Select, Button, ErrorBanner, StatCard } from '../components/UI'
import { CheckCircle2 } from 'lucide-react'

const LOCALITIES = [
  'Velachery','Anna Nagar','Adyar','T Nagar','Porur',
  'Chromepet','Sholinganallur','Perambur','Korattur',
  'Medavakkam','Tambaram','Mylapore','Nungambakkam','Kodambakkam','OMR'
].map(l => ({ value: l, label: l }))

const initForm = {
  locality: 'Velachery', sqft: '', bhk: '2',
  furnishing: 'semi', water_source: 'metro', age: '',
  rent: '', bachelor_friendly: false, pet_friendly: false,
}

export default function Landlord() {
  const [form,    setForm]    = useState(initForm)
  const [result,  setResult]  = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async () => {
    setError(''); setResult(null)
    if (!form.sqft || !form.age || !form.rent) { setError('Please fill in all fields.'); return }
    setLoading(true)
    try {
      const payload = {
        locality:          form.locality,
        sqft:              Number(form.sqft),
        bhk:               Number(form.bhk),
        furnishing:        form.furnishing,
        water_source:      form.water_source,
        age:               Number(form.age),
        rent:              Number(form.rent),
        bachelor_friendly: form.bachelor_friendly,
        pet_friendly:      form.pet_friendly,
      }
      const { data } = await addProperty(payload)
      setResult(data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Something went wrong. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">

      {/* Header */}
      <div className="mb-10 fade-up">
        <p className="text-xs font-mono uppercase tracking-widest mb-2" style={{ color: 'var(--accent2)' }}>
          Landlord Portal
        </p>
        <h1 className="font-display font-bold text-3xl">List your property</h1>
        <p className="mt-2 text-sm" style={{ color: 'var(--muted)' }}>
          Add your listing and let tenants find it — our AI will analyze it for them.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Form */}
        <Card className="fade-up-2 flex flex-col gap-5">
          <Select label="Locality" value={form.locality}
                  onChange={e => set('locality', e.target.value)} options={LOCALITIES} />
          <div className="grid grid-cols-2 gap-3">
            <Input label="Sqft" type="number" placeholder="1200"
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
          <Input label="Building Age (years)" type="number" placeholder="3"
                 value={form.age} onChange={e => set('age', e.target.value)} />
          <Input label="Your Listed Rent (₹)" type="number" placeholder="25000"
                 value={form.rent} onChange={e => set('rent', e.target.value)} />

          {/* Toggles */}
          <div className="flex gap-4">
            {[['bachelor_friendly','Bachelor Friendly'],['pet_friendly','Pet Friendly']].map(([k, label]) => (
              <button key={k} onClick={() => set(k, !form[k])}
                      className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm transition-all"
                      style={{
                        background: form[k] ? 'rgba(110,231,183,0.1)' : 'var(--surface2)',
                        border: `1px solid ${form[k] ? 'rgba(110,231,183,0.3)' : 'var(--border)'}`,
                        color: form[k] ? 'var(--accent)' : 'var(--muted)',
                      }}>
                <span>{form[k] ? '✓' : '+'}</span> {label}
              </button>
            ))}
          </div>

          <ErrorBanner message={error} />

          <Button loading={loading} onClick={handleSubmit}>
            {loading ? 'Listing...' : '→ List Property'}
          </Button>
        </Card>

        {/* Success / Preview */}
        <div className="fade-up-3">
          {!result ? (
            <div className="h-full flex items-center justify-center rounded-2xl"
                 style={{ border: '1px dashed var(--border)', minHeight: 300 }}>
              <div className="text-center">
                <div className="text-4xl mb-3">🏢</div>
                <p className="text-sm" style={{ color: 'var(--muted)' }}>
                  Your listing preview will appear here.
                </p>
              </div>
            </div>
          ) : (
            <Card className="flex flex-col gap-5">
              <div className="flex items-center gap-3">
                <CheckCircle2 size={22} style={{ color: 'var(--accent)' }} />
                <div>
                  <p className="font-display font-semibold">Property Listed!</p>
                  <p className="text-xs" style={{ color: 'var(--muted)' }}>ID #{result.id} · visible in marketplace</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <StatCard icon="📍" label="Locality" value={result.locality} />
                <StatCard icon="📐" label="Size" value={`${result.sqft} sqft`} sub={`${result.bhk} BHK`} />
                <StatCard icon="💰" label="Listed Rent" accent value={`₹${result.rent.toLocaleString('en-IN')}`} />
                <StatCard icon="🛋" label="Furnishing" value={result.furnishing} />
              </div>

              <div className="flex gap-2 flex-wrap">
                {result.bachelor_friendly && (
                  <span className="px-3 py-1 rounded-lg text-xs"
                        style={{ background: 'rgba(110,231,183,0.1)', color: 'var(--accent)', border: '1px solid rgba(110,231,183,0.2)' }}>
                    ✓ Bachelor Friendly
                  </span>
                )}
                {result.pet_friendly && (
                  <span className="px-3 py-1 rounded-lg text-xs"
                        style={{ background: 'rgba(129,140,248,0.1)', color: 'var(--accent2)', border: '1px solid rgba(129,140,248,0.2)' }}>
                    ✓ Pet Friendly
                  </span>
                )}
              </div>

              <p className="text-xs" style={{ color: 'var(--muted)' }}>
                Tenants can now find and analyze your listing. The AI will automatically compare your rent to market predictions.
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}