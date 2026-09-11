import type { Incident } from '../types'

export function IncidentFeed({ incidents, onSelect }: { incidents: Incident[]; onSelect: (incident: Incident) => void }) {
  return <aside className="panel feed-panel">
    <div className="panel-title">Live incidents</div>
    <div className="feed-list">
      {incidents.map(i => <button className="incident-card" key={i.id} onClick={() => onSelect(i)}>
        <div className="incident-row"><strong>{i.title}</strong><span className={`status ${i.status.toLowerCase()}`}>{i.status}</span></div>
        <p>{i.summary}</p>
        <div className="incident-meta"><span>{Math.round(i.confidence * 100)}% confidence</span><span>{i.source_count} sources</span></div>
      </button>)}
    </div>
  </aside>
}
