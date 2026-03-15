import { useState, useEffect } from 'react'
import { Bell, RefreshCw, Zap } from 'lucide-react'
import api from '../api'
import StatusBadge from '../components/StatusBadge'
import SeverityDot from '../components/SeverityDot'
import { formatDistanceToNow } from 'date-fns'

export default function Alerts() {
  const [alerts, setAlerts] = useState([])
  const [services, setServices] = useState([])
  const [loading, setLoading] = useState(true)
  const [showTrigger, setShowTrigger] = useState(false)
  const [routingKey, setRoutingKey] = useState('')
  const [summary, setSummary] = useState('')
  const [severity, setSeverity] = useState('critical')
  const [source, setSource] = useState('')
  const [message, setMessage] = useState('')

  const fetch = () => {
    setLoading(true)
    Promise.all([api.get('/alerts/'), api.get('/services')]).then(([a, s]) => {
      setAlerts(a.data)
      setServices(s.data)
    }).finally(() => setLoading(false))
  }

  useEffect(() => { fetch() }, [])

  const triggerAlert = async (e) => {
    e.preventDefault()
    setMessage('')
    try {
      await api.post('/alerts/events', {
        routing_key: routingKey,
        event_action: 'trigger',
        payload: { summary, severity, source, custom_details: {} },
      })
      setMessage('Alert triggered successfully!')
      fetch()
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Error triggering alert')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Alerts</h1>
          <p className="text-gray-500 text-sm mt-1">{alerts.length} recent alerts</p>
        </div>
        <div className="flex items-center space-x-2">
          <button onClick={fetch} className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg">
            <RefreshCw size={16} />
          </button>
          <button
            onClick={() => setShowTrigger(true)}
            className="flex items-center space-x-2 bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            <Zap size={16} />
            <span>Trigger Alert</span>
          </button>
        </div>
      </div>

      {/* Integration key helper */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm">
        <p className="font-medium text-blue-800 mb-1">Events API v2 Endpoint</p>
        <code className="text-blue-700">POST /api/alerts/events</code>
        <p className="text-blue-600 mt-1 text-xs">Use a service integration key as the routing_key. Supports trigger, resolve, and acknowledge actions.</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        {loading ? (
          <div className="text-center py-12 text-gray-400">Loading…</div>
        ) : alerts.length === 0 ? (
          <div className="text-center py-12 text-gray-400">No alerts yet</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50">
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Alert</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Source</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Incident</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden lg:table-cell">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {alerts.map((alert) => (
                <tr key={alert.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-2">
                      <SeverityDot severity={alert.severity} />
                      <span className="font-medium text-gray-900 truncate max-w-xs">{alert.summary || 'No summary'}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-gray-500 hidden sm:table-cell">{alert.source || '—'}</td>
                  <td className="px-6 py-4"><StatusBadge status={alert.status} /></td>
                  <td className="px-6 py-4 text-gray-500 hidden md:table-cell">
                    {alert.incident_id ? `#${alert.incident_id}` : '—'}
                  </td>
                  <td className="px-6 py-4 text-gray-400 hidden lg:table-cell">
                    {formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showTrigger && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg">
            <div className="px-6 py-4 border-b border-gray-100">
              <h2 className="text-lg font-semibold">Trigger Alert</h2>
            </div>
            <form onSubmit={triggerAlert} className="p-6 space-y-4">
              {message && (
                <div className={`p-3 rounded-lg text-sm ${message.includes('Error') || message.includes('Invalid') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
                  {message}
                </div>
              )}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Routing Key (Service Integration Key)</label>
                <select className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
                  value={routingKey} onChange={(e) => setRoutingKey(e.target.value)} required>
                  <option value="">Select service…</option>
                  {services.map((s) => <option key={s.id} value={s.integration_key}>{s.name} ({s.integration_key.slice(0, 8)}…)</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Summary</label>
                <input className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
                  value={summary} onChange={(e) => setSummary(e.target.value)} required />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Severity</label>
                  <select className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
                    value={severity} onChange={(e) => setSeverity(e.target.value)}>
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="warning">Warning</option>
                    <option value="info">Info</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Source</label>
                  <input className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
                    placeholder="e.g. server-01" value={source} onChange={(e) => setSource(e.target.value)} />
                </div>
              </div>
              <div className="flex justify-end space-x-3 pt-2">
                <button type="button" onClick={() => { setShowTrigger(false); setMessage('') }} className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg text-sm">Close</button>
                <button type="submit" className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm font-medium">Trigger</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
