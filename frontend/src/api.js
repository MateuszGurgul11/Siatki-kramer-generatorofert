const BASE_URL = import.meta.env.VITE_API_URL || '/api'

export async function fetchNets() {
  const res = await fetch(`${BASE_URL}/nets`)
  if (!res.ok) throw new Error('Błąd pobierania siatek')
  return res.json()
}

export async function calculateQuote(data) {
  const res = await fetch(`${BASE_URL}/calculate`, {
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
  const res = await fetch(`${BASE_URL}/generate-offer`, {
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
