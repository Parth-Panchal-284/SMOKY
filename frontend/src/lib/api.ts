import type { Incident, Shelter, Zone } from '../types'

const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${BASE}${path}`)
  if (!response.ok) throw new Error(`Request failed: ${response.status}`)
  return response.json()
}

export const api = {
  zones: () => getJson<Zone[]>('/api/zones'),
  incidents: () => getJson<Incident[]>('/api/incidents'),
  shelters: () => getJson<Shelter[]>('/api/shelters'),
  chat: async (message: string) => {
    const response = await fetch(`${BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, lat: 37.3352, lng: -121.8811 })
    })
    if (!response.ok) throw new Error(`Request failed: ${response.status}`)
    return response.json() as Promise<{ answer: string; incident_ids: string[]; suggested_action?: string }>
  }
}
