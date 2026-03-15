import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Filter, RefreshCw } from 'lucide-react'
import api from '../api'
import StatusBadge from '../components/StatusBadge'
import SeverityDot from '../components/SeverityDot'
import { formatDistanceToNow } from 'date-fns'

const STATUS_TABS = ['all', 'triggered', 'acknowledged', 'resolved']

export default function Incidents() {
  const [incidents, setIncidents] = useState([])
  const [tab, setTab] = useState('all')
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [services, setServices] = useState([])
  const [form, setForm] = useState({ title: '', description: '', severity: 'critical', service_id: '' })

  const fetchIncidents = () => {
    setLoading(true)
    const params = tab !== 'all' ? `?status=${tab}` : ''
    api.get(`/incidents${params}`).then((res) => setIncidents(res.data)).finally(() => setLoading(false))
  }

  useEffect(() => { fetchIncidents() }, [tab])
  useEffect(() => { api.get('/services').then((res) => setServices(res.data)) }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    await api.post('/incidents', { ...form, service_id: parseInt(form.service_id) })
    setShowCreate(false)
    setForm({ title: '', description: '', severity: 'critical', service_id: '' })
    fetchIncidents()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Incidents</h1>
          <p className="text-gray-500 text-sm mt-1">{incidents.length} incidents</p>
        </div>
        <div className="flex items-center space-x-2">
          <button onClick={fetchIncidents} className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg">
            <RefreshCw size={16} />
          </button>
          <button
            onClick={() => setShowCreate(true)}
            className="flex items-center space-x-2 bg-[#06AC38] hover:bg-[#058A2E] text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            <Plus size={16} />
            <span>Create Incident</span>
          </button>
        </div>
      </div>

      {/* Status tabs */}
      <div className="flex space-x-1 bg-gray-100 rounded-lg p-1 w-fit">
        {STATUS_TABS.map((s) => (
          <button
            key={s}
            onClick={() => setTab(s)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium capitalize transition-colors ${
              tab === s ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        {loading ? (
          <div className="text-center py-12 text-gray-400">Loading…</div>
        ) : incidents.length === 0 ? (
          <div className="text-center py-12 text-gray-400">No incidents found</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50 text-left">
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Incident</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider hidden sm:table-cell">Service</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider hidden md:table-cell">Assigned</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider hidden lg:table-cell">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {incidents.map((inc) => (
                <tr key={inc.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-3">
                      <SeverityDot severity={inc.severity} />
                      <div>
                        <Link to={`/incidents/${inc.id}`} className="font-medium text-gray-900 hover:text-[#06AC38]">
                          #{inc.incident_number} {inc.title}
                        </Link>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-gray-500 hidden sm:table-cell">{inc.service?.name}</td>
                  <td className="px-6 py-4 text-gray-500 hidden md:table-cell">{inc.assigned_to?.name || '—'}</td>
                  <td className="px-6 py-4"><StatusBadge status={inc.status} /></td>
                  <td className="px-6 py-4 text-gray-400 hidden lg:table-cell">{formatDistanceToNow(new Date(inc.created_at), { addSuffix: true })}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg">
            <div className="px-6 py-4 border-b border-gray-100">
              <h2 className="text-lg font-semibold">Create Incident</h2>
            </div>
            <form onSubmit={handleCreate} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Service</label>
                <select
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
                  value={form.service_id}
                  onChange={(e) => setForm({ ...form, service_id: e.target.value })}
                  required
                >
                  <option value="">Select service…</option>
                  {services.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Severity</label>
                <select
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
                  value={form.severity}
                  onChange={(e) => setForm({ ...form, severity: e.target.value })}
                >
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="warning">Warning</option>
                  <option value="info">Info</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
                  rows={3}
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                />
              </div>
              <div className="flex justify-end space-x-3 pt-2">
                <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg text-sm">
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 bg-[#06AC38] hover:bg-[#058A2E] text-white rounded-lg text-sm font-medium">
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
