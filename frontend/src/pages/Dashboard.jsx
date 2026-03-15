import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { AlertTriangle, CheckCircle, Clock, Server, Users, Activity } from 'lucide-react'
import api from '../api'
import StatusBadge from '../components/StatusBadge'
import SeverityDot from '../components/SeverityDot'
import { formatDistanceToNow } from 'date-fns'

function StatCard({ title, value, icon: Icon, color, subtitle }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}`}>
          <Icon size={20} className="text-white" />
        </div>
      </div>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
      {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
    </div>
  )
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [incidents, setIncidents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/dashboard/stats'),
      api.get('/incidents?status=triggered'),
    ]).then(([statsRes, incidentsRes]) => {
      setStats(statsRes.data)
      setIncidents(incidentsRes.data.slice(0, 10))
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex items-center justify-center h-64 text-gray-400">Loading…</div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">Real-time incident & on-call overview</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard title="Total Incidents" value={stats?.total_incidents || 0} icon={Activity} color="bg-gray-600" />
        <StatCard title="Triggered" value={stats?.triggered_incidents || 0} icon={AlertTriangle} color="bg-red-500" subtitle="Needs attention" />
        <StatCard title="Acknowledged" value={stats?.acknowledged_incidents || 0} icon={Clock} color="bg-yellow-500" subtitle="Being worked on" />
        <StatCard title="Resolved" value={stats?.resolved_incidents || 0} icon={CheckCircle} color="bg-green-500" subtitle="Closed" />
        <StatCard title="Services" value={stats?.total_services || 0} icon={Server} color="bg-blue-500" subtitle={`${stats?.services_with_incidents || 0} with issues`} />
        <StatCard title="On-Call" value={stats?.on_call_users || 0} icon={Users} color="bg-purple-500" subtitle="Currently on-call" />
      </div>

      {/* Active incidents */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Active Incidents</h2>
          <Link to="/incidents" className="text-sm text-[#06AC38] hover:underline">View all →</Link>
        </div>
        {incidents.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-gray-400">
            <CheckCircle size={48} className="text-green-400 mb-3" />
            <p className="font-medium">All clear!</p>
            <p className="text-sm">No active incidents</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {incidents.map((incident) => (
              <Link
                key={incident.id}
                to={`/incidents/${incident.id}`}
                className="flex items-center px-6 py-4 hover:bg-gray-50 transition-colors"
              >
                <SeverityDot severity={incident.severity} />
                <div className="ml-3 flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    #{incident.incident_number} — {incident.title}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {incident.service?.name} · {formatDistanceToNow(new Date(incident.created_at), { addSuffix: true })}
                  </p>
                </div>
                <StatusBadge status={incident.status} />
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
