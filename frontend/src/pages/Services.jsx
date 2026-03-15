import { useState, useEffect } from 'react'
import { Plus, Server, Copy, Check } from 'lucide-react'
import api from '../api'
import StatusBadge from '../components/StatusBadge'

export default function Services() {
  const [services, setServices] = useState([])
  const [policies, setPolicies] = useState([])
  const [teams, setTeams] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [copiedKey, setCopiedKey] = useState(null)
  const [form, setForm] = useState({ name: '', description: '', escalation_policy_id: '', team_id: '' })

  useEffect(() => {
    Promise.all([
      api.get('/services'),
      api.get('/escalation-policies'),
      api.get('/teams'),
    ]).then(([s, p, t]) => {
      setServices(s.data)
      setPolicies(p.data)
      setTeams(t.data)
    }).finally(() => setLoading(false))
  }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    const payload = { ...form }
    if (payload.escalation_policy_id) payload.escalation_policy_id = parseInt(payload.escalation_policy_id)
    if (payload.team_id) payload.team_id = parseInt(payload.team_id)
    const res = await api.post('/services', payload)
    setServices([...services, res.data])
    setShowCreate(false)
    setForm({ name: '', description: '', escalation_policy_id: '', team_id: '' })
  }

  const copyKey = (key) => {
    navigator.clipboard.writeText(key)
    setCopiedKey(key)
    setTimeout(() => setCopiedKey(null), 2000)
  }

  if (loading) return <div className="text-center py-12 text-gray-400">Loading…</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Services</h1>
          <p className="text-gray-500 text-sm mt-1">{services.length} services configured</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center space-x-2 bg-[#06AC38] hover:bg-[#058A2E] text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          <Plus size={16} />
          <span>New Service</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {services.map((service) => (
          <div key={service.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                  <Server size={18} className="text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{service.name}</h3>
                  <StatusBadge status={service.status} />
                </div>
              </div>
            </div>
            {service.description && (
              <p className="text-sm text-gray-500 mb-3">{service.description}</p>
            )}
            <div className="flex items-center space-x-2 bg-gray-50 rounded-lg px-3 py-2">
              <code className="text-xs text-gray-600 flex-1 truncate font-mono">{service.integration_key}</code>
              <button onClick={() => copyKey(service.integration_key)} className="text-gray-400 hover:text-gray-600 flex-shrink-0">
                {copiedKey === service.integration_key ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
              </button>
            </div>
          </div>
        ))}
      </div>

      {showCreate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg">
            <div className="px-6 py-4 border-b border-gray-100">
              <h2 className="text-lg font-semibold">Create Service</h2>
            </div>
            <form onSubmit={handleCreate} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
                  value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
                  rows={2} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Escalation Policy</label>
                <select className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
                  value={form.escalation_policy_id} onChange={(e) => setForm({ ...form, escalation_policy_id: e.target.value })}>
                  <option value="">None</option>
                  {policies.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Team</label>
                <select className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
                  value={form.team_id} onChange={(e) => setForm({ ...form, team_id: e.target.value })}>
                  <option value="">None</option>
                  {teams.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
                </select>
              </div>
              <div className="flex justify-end space-x-3 pt-2">
                <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg text-sm">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-[#06AC38] hover:bg-[#058A2E] text-white rounded-lg text-sm font-medium">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
