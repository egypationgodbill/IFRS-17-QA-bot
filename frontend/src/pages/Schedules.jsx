import { useState, useEffect } from 'react'
import { Calendar, Clock, Plus, Users } from 'lucide-react'
import api from '../api'
import { format } from 'date-fns'

export default function Schedules() {
  const [schedules, setSchedules] = useState([])
  const [oncall, setOncall] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [users, setUsers] = useState([])
  const [teams, setTeams] = useState([])
  const [form, setForm] = useState({ name: '', description: '', time_zone: 'UTC', team_id: '' })

  useEffect(() => {
    Promise.all([
      api.get('/schedules'),
      api.get('/schedules/oncall'),
      api.get('/users'),
      api.get('/teams'),
    ]).then(([s, oc, u, t]) => {
      setSchedules(s.data)
      setOncall(oc.data)
      setUsers(u.data)
      setTeams(t.data)
    }).finally(() => setLoading(false))
  }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    const payload = { ...form, layers: [] }
    if (payload.team_id) payload.team_id = parseInt(payload.team_id)
    const res = await api.post('/schedules', payload)
    setSchedules([...schedules, res.data])
    setShowCreate(false)
  }

  if (loading) return <div className="text-center py-12 text-gray-400">Loading…</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Schedules</h1>
          <p className="text-gray-500 text-sm mt-1">On-call rotation management</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center space-x-2 bg-[#06AC38] hover:bg-[#058A2E] text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          <Plus size={16} />
          <span>New Schedule</span>
        </button>
      </div>

      {/* Currently on-call */}
      {oncall.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-5">
          <h2 className="font-semibold text-green-800 mb-3 flex items-center space-x-2">
            <Clock size={16} />
            <span>Currently On-Call</span>
          </h2>
          <div className="flex flex-wrap gap-3">
            {oncall.map((shift) => (
              <div key={shift.id} className="flex items-center space-x-2 bg-white border border-green-200 rounded-lg px-3 py-2">
                <div className="w-7 h-7 bg-[#06AC38] rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">{shift.user?.name?.[0]}</span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">{shift.user?.name}</p>
                  <p className="text-xs text-gray-500">Until {format(new Date(shift.end), 'MMM d, HH:mm')}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Schedule list */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {schedules.map((schedule) => (
          <div key={schedule.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-10 h-10 bg-purple-50 rounded-lg flex items-center justify-center">
                <Calendar size={18} className="text-purple-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{schedule.name}</h3>
                <p className="text-xs text-gray-500">{schedule.time_zone}</p>
              </div>
            </div>
            {schedule.description && <p className="text-sm text-gray-500 mb-3">{schedule.description}</p>}
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <Users size={14} />
              <span>{schedule.layers?.length || 0} rotation layer{schedule.layers?.length !== 1 ? 's' : ''}</span>
            </div>
          </div>
        ))}
        {schedules.length === 0 && (
          <div className="col-span-2 text-center py-12 text-gray-400 bg-white rounded-xl border border-gray-100">
            No schedules configured. Create one to start managing on-call rotations.
          </div>
        )}
      </div>

      {showCreate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg">
            <div className="px-6 py-4 border-b border-gray-100">
              <h2 className="text-lg font-semibold">Create Schedule</h2>
            </div>
            <form onSubmit={handleCreate} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
                  value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Time Zone</label>
                <input className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
                  value={form.time_zone} onChange={(e) => setForm({ ...form, time_zone: e.target.value })} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Team</label>
                <select className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
                  value={form.team_id} onChange={(e) => setForm({ ...form, team_id: e.target.value })}>
                  <option value="">None</option>
                  {teams.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
                  rows={2} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
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
