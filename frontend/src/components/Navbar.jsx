// components/Navbar.jsx

import { Link, useLocation } from 'react-router-dom'

export default function Navbar() {
  const { pathname } = useLocation()

  const links = [
    { to: '/listings', label: 'Listings' },
    { to: '/tenant',   label: 'Analyze Rent' },
    { to: '/landlord', label: 'List Property' },
  ]

  return (
    <nav style={{ background: 'var(--surface)', borderBottom: '1px solid var(--border)' }}
         className="sticky top-0 z-50 px-6 py-4 flex items-center justify-between">

      <Link to="/" className="font-display font-bold text-lg tracking-tight"
            style={{ color: 'var(--accent)' }}>
        Search<span style={{ color: 'var(--text)' }}>Estate</span>
      </Link>

      <div className="flex items-center gap-1">
        {links.map(l => (
          <Link key={l.to} to={l.to}
                className="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
                style={{
                  background:  pathname === l.to ? 'var(--surface2)' : 'transparent',
                  color:       pathname === l.to ? 'var(--accent)'   : 'var(--muted)',
                  border:      pathname === l.to ? '1px solid var(--border)' : '1px solid transparent',
                }}>
            {l.label}
          </Link>
        ))}
      </div>
    </nav>
  )
}