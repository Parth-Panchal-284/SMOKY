import type { Incident, Shelter, Zone } from '../types'

const bounds = { minLat: 37.27, maxLat: 37.46, minLng: -122.02, maxLng: -121.78 }
function position(lat: number, lng: number) {
  const left = ((lng - bounds.minLng) / (bounds.maxLng - bounds.minLng)) * 100
  const top = (1 - (lat - bounds.minLat) / (bounds.maxLat - bounds.minLat)) * 100
  return { left: `${left}%`, top: `${top}%` }
}

export function DisasterMap({ zones, incidents, shelters, onIncident }: { zones: Zone[]; incidents: Incident[]; shelters: Shelter[]; onIncident: (i: Incident) => void }) {
  return <section className="map-card">
    <div className="map-label">San Jose live situation map <span>SIMULATED DATA</span></div>
    <div className="map-grid">
      <div className="map-road road-a"/><div className="map-road road-b"/><div className="map-road road-c"/>
      {zones.map(z => <div key={z.id} className={`zone-bubble ${z.risk_level.toLowerCase()}`} style={position(z.center_lat, z.center_lng)} title={`${z.name}: ${z.risk_level}`}><span>{z.id}</span></div>)}
      {incidents.map(i => <button key={i.id} className={`map-pin severity-${i.severity}`} style={position(i.lat, i.lng)} onClick={() => onIncident(i)} title={i.title}>!</button>)}
      {shelters.map(s => <div key={s.id} className="shelter-pin" style={position(s.lat, s.lng)} title={`${s.name}: ${s.available_capacity} spaces`}>+</div>)}
      <div className="you-pin" style={position(37.3352, -121.8811)}>YOU</div>
    </div>
    <div className="map-legend"><span>! Incident</span><span>+ Shelter</span><span>Zones are geographic analysis units</span></div>
  </section>
}
