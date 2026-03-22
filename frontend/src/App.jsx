// App.jsx — routing

import { Routes, Route } from 'react-router-dom'
import Navbar         from './components/Navbar'
import Home           from './pages/Home'
import Tenant         from './pages/Tenant'
import Landlord       from './pages/Landlord'
import Listings       from './pages/Listings'
import PropertyDetail from './pages/PropertyDetail'

export default function App() {
  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>
      <Navbar />
      <Routes>
        <Route path="/"              element={<Home />} />
        <Route path="/tenant"        element={<Tenant />} />
        <Route path="/landlord"      element={<Landlord />} />
        <Route path="/listings"      element={<Listings />} />
        <Route path="/property/:id"  element={<PropertyDetail />} />
      </Routes>
    </div>
  )
}