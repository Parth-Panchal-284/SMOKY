import type { Incident } from '../types'

export function IncidentDrawer({ incident, onClose }: { incident?: Incident; onClose: () => void }) {
  if (!incident) return null
  return <div className="drawer-backdrop" onClick={onClose}>
    <section className="drawer" onClick={e => e.stopPropagation()}>
      <button className="close" onClick={onClose}>×</button>
      <div className="eyebrow">{incident.id} · {incident.zone_id}</div>
      <h2>{incident.title}</h2>
      <div className="drawer-stats">
        <div><strong>{Math.round(incident.confidence * 100)}%</strong><small>confidence</small></div>
        <div><strong>{incident.source_count}</strong><small>sources</small></div>
        <div><strong>{incident.severity}/5</strong><small>severity</small></div>
      </div>
      <p>{incident.summary}</p>
      <div className="evidence-box">
        <strong>{incident.official_confirmation ? 'Official/responder confirmation present' : 'No official confirmation yet'}</strong>
        <span>Status: {incident.status}</span>
        <span>Evidence IDs: {incident.evidence_report_ids.join(', ')}</span>
      </div>
    </section>
  </div>
}
