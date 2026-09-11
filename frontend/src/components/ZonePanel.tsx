import type { Zone } from '../types'

export function ZonePanel({ zones, selected, onSelect }: { zones: Zone[]; selected?: string; onSelect: (id: string) => void }) {
  return <aside className="panel zone-panel">
    <div className="panel-title">Zones</div>
    {zones.map(zone => <button key={zone.id} className={`zone-card ${selected === zone.id ? 'selected' : ''}`} onClick={() => onSelect(zone.id)}>
      <div><strong>{zone.name}</strong><span className={`risk ${zone.risk_level.toLowerCase()}`}>{zone.risk_level}</span></div>
      <small>{zone.incident_count} active incident{zone.incident_count === 1 ? '' : 's'}</small>
    </button>)}
  </aside>
}
