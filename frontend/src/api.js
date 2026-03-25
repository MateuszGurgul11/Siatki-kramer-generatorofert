/**
 * Origin backendu (Render), np. https://xxx.onrender.com — USTAW w Vercel jako VITE_API_URL.
 * Endpointy FastAPI są pod /api/..., stąd doklejamy /api.
 * Lokalnie (Vite): proxy /api → localhost:8000, więc używamy względnego "/api".
 */
const API_ORIGIN = (import.meta.env.VITE_API_URL || '').trim().replace(/\/$/, '')
export const API_BASE = API_ORIGIN ? `${API_ORIGIN}/api` : '/api'

/** Ścieżka względna z API (np. /api/offers/.../pdf) → pełny URL na produkcji */
export function resolveApiUrl(path) {
  if (!path || path.startsWith('http')) return path
  const o = API_ORIGIN
  if (o) return `${o}${path.startsWith('/') ? path : `/${path}`}`
  return path
}

export async function fetchNets() {
  const res = await fetch(`${API_BASE}/nets`)
  if (!res.ok) throw new Error('Błąd pobierania siatek')
  return res.json()
}

export async function calculateQuote(data) {
  const res = await fetch(`${API_BASE}/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Błąd kalkulacji')
  }
  return res.json()
}

export async function generateOffer(data) {
  const res = await fetch(`${API_BASE}/generate-offer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Błąd generowania oferty')
  }
  return res.json()
}
