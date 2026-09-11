import { useEffect, useMemo, useState } from 'react'
import { api } from './lib/api'
import type { Incident, Shelter, Zone } from './types'
import { ZonePanel } from './components/ZonePanel'
import { IncidentFeed } from './components/IncidentFeed'
import { DisasterMap } from './components/DisasterMap'
import { IncidentDrawer } from './components/IncidentDrawer'
import { DisasterChat } from './components/DisasterChat'
import './styles.css'

export default function App() {
  const [zones, setZones] = useState<Zone[]>([])
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [shelters, setShelters] = useState<Shelter[]>([])
  const [zoneId, setZoneId] = useState<string>()
  const [selectedIncident, setSelectedIncident] = useState<Incident>()
  const [error, setError] = useState<string>()

  useEffect(() => {
    Promise.all([api.zones(), api.incidents(), api.shelters()])
      .then(([z, i, s]) => { setZones(z); setIncidents(i); setShelters(s) })
      .catch(() => setError('Backend unavailable. Start FastAPI on port 8000.'))
  }, [])

  const visible = useMemo(() => zoneId ? incidents.filter(i => i.zone_id === zoneId) : incidents, [incidents, zoneId])
  const critical = incidents.filter(i => i.severity >= 4).length

  return <main>
    <header className="topbar">
      <div><div className="brand">SMOKY</div><h1>Disaster Intelligence Center</h1></div>
      <div className="header-stats"><div><strong>{incidents.length}</strong><span>active incidents</span></div><div><strong>{critical}</strong><span>high severity</span></div><div><strong>4</strong><span>zones</span></div></div>
      <div className="demo-pill">SIMULATION · SAN JOSE</div>
    </header>
    {error && <div className="error-banner">{error}</div>}
    <section className="workspace">
      <ZonePanel zones={zones} selected={zoneId} onSelect={id => setZoneId(current => current === id ? undefined : id)} />
      <div className="center-column">
        <DisasterMap zones={zones} incidents={visible} shelters={shelters} onIncident={setSelectedIncident} />
        <DisasterChat />
      </div>
      <IncidentFeed incidents={visible} onSelect={setSelectedIncident} />
    </section>
    <IncidentDrawer incident={selectedIncident} onClose={() => setSelectedIncident(undefined)} />
  </main>
}
