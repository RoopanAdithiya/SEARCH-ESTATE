// pages/Home.jsx

import { useNavigate } from 'react-router-dom'
import { Building2, Search, ArrowRight } from 'lucide-react'

export default function Home() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 relative overflow-hidden">

      {/* Background glow blobs */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full pointer-events-none"
           style={{ background: 'radial-gradient(circle, rgba(110,231,183,0.05) 0%, transparent 70%)' }} />
      <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] rounded-full pointer-events-none"
           style={{ background: 'radial-gradient(circle, rgba(129,140,248,0.05) 0%, transparent 70%)' }} />

      {/* Hero text */}
      <div className="text-center mb-16 fade-up max-w-2xl">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-mono mb-6"
             style={{ background: 'var(--surface2)', border: '1px solid var(--border)', color: 'var(--accent)' }}>
          <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
          AI-Powered Rent Intelligence · Chennai
        </div>

        <h1 className="font-display font-extrabold text-5xl leading-none tracking-tight mb-4"
            style={{ color: 'var(--text)' }}>
          Know the real<br />
          <span style={{ color: 'var(--accent)' }}>price of rent.</span>
        </h1>

        <p className="text-base max-w-md mx-auto" style={{ color: 'var(--muted)' }}>
          Stop guessing. Our ML model predicts fair rent, detects overpricing,
          and tells you if a property is worth it — before you sign anything.
        </p>
      </div>

      {/* Two big choice cards — tenant is dominant */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-2xl fade-up-2">

        {/* Tenant — PRIMARY, dominant */}
        <button onClick={() => navigate('/tenant')}
                className="group text-left p-8 rounded-2xl transition-all duration-300 relative overflow-hidden"
                style={{
                  background: 'linear-gradient(135deg, rgba(110,231,183,0.08) 0%, var(--surface) 60%)',
                  border: '1px solid rgba(110,231,183,0.35)',
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.border = '1px solid rgba(110,231,183,0.7)'
                  e.currentTarget.style.background = 'linear-gradient(135deg, rgba(110,231,183,0.13) 0%, var(--surface2) 60%)'
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.border = '1px solid rgba(110,231,183,0.35)'
                  e.currentTarget.style.background = 'linear-gradient(135deg, rgba(110,231,183,0.08) 0%, var(--surface) 60%)'
                }}>
          {/* "Most popular" nudge */}
          <div className="absolute top-4 right-4 px-2 py-0.5 rounded-full text-xs font-mono"
               style={{ background: 'rgba(110,231,183,0.15)', color: 'var(--accent)', border: '1px solid rgba(110,231,183,0.3)' }}>
            Most used
          </div>
          <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-6"
               style={{ background: 'rgba(110,231,183,0.15)', border: '1px solid rgba(110,231,183,0.3)' }}>
            <Search size={18} style={{ color: 'var(--accent)' }} />
          </div>
          <h2 className="font-display font-bold text-xl mb-2">I'm a Tenant</h2>
          <p className="text-sm mb-6" style={{ color: 'var(--muted)' }}>
            Analyze any listing. Find out if you're being overcharged before you commit.
          </p>
          <div className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all"
               style={{ background: 'var(--accent)', color: '#0a0a0f' }}>
            Analyze a property <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
          </div>
        </button>

        {/* Landlord — secondary */}
        <button onClick={() => navigate('/landlord')}
                className="group text-left p-8 rounded-2xl transition-all duration-300"
                style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}
                onMouseEnter={e => {
                  e.currentTarget.style.borderColor = 'var(--accent2)'
                  e.currentTarget.style.background = 'var(--surface2)'
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.borderColor = 'var(--border)'
                  e.currentTarget.style.background = 'var(--surface)'
                }}>
          <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-6"
               style={{ background: 'rgba(129,140,248,0.1)', border: '1px solid rgba(129,140,248,0.2)' }}>
            <Building2 size={18} style={{ color: 'var(--accent2)' }} />
          </div>
          <h2 className="font-display font-bold text-xl mb-2">I'm a Landlord</h2>
          <p className="text-sm mb-6" style={{ color: 'var(--muted)' }}>
            List your property and get an AI-optimized rent recommendation instantly.
          </p>
          <div className="flex items-center gap-2 text-sm font-medium"
               style={{ color: 'var(--accent2)' }}>
            List a property <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
          </div>
        </button>
      </div>

      {/* Bottom link to listings */}
      <div className="mt-8 fade-up-3">
        <button onClick={() => navigate('/listings')}
                className="text-sm transition-colors"
                style={{ color: 'var(--muted)' }}
                onMouseEnter={e => e.target.style.color = 'var(--text)'}
                onMouseLeave={e => e.target.style.color = 'var(--muted)'}>
          Browse all listings →
        </button>
      </div>
    </div>
  )
}