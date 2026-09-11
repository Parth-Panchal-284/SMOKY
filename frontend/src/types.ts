export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

export interface Zone {
  id: string
  name: string
  center_lat: number
  center_lng: number
  risk_level: RiskLevel
  incident_count: number
}

export interface Incident {
  id: string
  zone_id: string
  title: string
  incident_type: string
  severity: number
  confidence: number
  status: 'UNVERIFIED' | 'CORROBORATED' | 'CONFIRMED' | 'RESOLVED'
  lat: number
  lng: number
  source_count: number
  official_confirmation: boolean
  summary: string
  last_updated: string
  evidence_report_ids: string[]
}

export interface Shelter {
  id: string
  name: string
  lat: number
  lng: number
  capacity: number
  available_capacity: number
  status: string
  zone_id: string
}
