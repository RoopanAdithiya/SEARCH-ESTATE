// services/api.js — single source of truth for all backend calls

import axios from 'axios'

const API = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  timeout: 10000,
})

// ── Interceptor: log errors globally ──────────────────────────────────────────
API.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error('API Error:', err.response?.data || err.message)
    return Promise.reject(err)
  }
)

export const getProperties   = ()     => API.get('/properties')
export const analyzeProperty = (id)   => API.get(`/analyze/${id}`)
export const predictRent     = (data) => API.post('/predict-rent', data)
export const addProperty     = (data) => API.post('/add-property', data)