import { useState } from 'react'
import { api } from '../lib/api'

export function DisasterChat() {
  const [message, setMessage] = useState('')
  const [answer, setAnswer] = useState('Ask about nearby hazards, shelters, or safe travel.')
  const [loading, setLoading] = useState(false)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    if (!message.trim()) return
    setLoading(true)
    try {
      const result = await api.chat(message)
      setAnswer(result.answer)
    } catch {
      setAnswer('The assistant is unavailable. Check the incident map and official instructions.')
    } finally {
      setLoading(false)
    }
  }

  return <section className="chat-card">
    <div><div className="panel-title">Disaster assistant</div><p className="assistant-answer">{answer}</p></div>
    <form onSubmit={submit}>
      <input value={message} onChange={e => setMessage(e.target.value)} placeholder="Can I safely drive to North San Jose?" />
      <button disabled={loading}>{loading ? 'Checking…' : 'Ask'}</button>
    </form>
  </section>
}
