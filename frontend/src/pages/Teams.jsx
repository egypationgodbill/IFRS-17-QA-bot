import { useState, useEffect } from 'react'
import { Plus, Users, UserPlus, UserMinus } from 'lucide-react'
import api from '../api'

export default function Teams() {
  const [teams, setTeams] = useState([])
  const [allUsers, setAllUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ name: '', description: '' })

  useEffect(() => {
    Promise.all([api.get('/teams'), api.get('/users')]).then(([t, u]) => {
      setTeams(t.data)
      setAllUsers(u.data)
    }).finally(() => setLoading(false))
  }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    const res = await api.post('/teams', form)
    setTeams([...teams, res.data])
    setShowCreate(false)
    setForm({ name: '', description: '' })
  }

  if (loading) return <div className="text-center py-12 text-gray-400">Loading…</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Teams</h1>
          <p className="text-gray-500 text-sm mt-1">{teams.length} teams</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center space-x-2 bg-[#06AC38] hover:bg-[#058A2E] text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          <Plus size={16} />
          <span>New Team</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {teams.map((team) => (
          <div key={team.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-10 h-10 bg-indigo-50 rounded-lg flex items-center justify-center">
                <Users size={18} className="text-indigo-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{team.name}</h3>
                <p className="text-xs text-gray-500">{team.members?.length || 0} members</p>
              </div>
            </div>
            {team.description && <p className="text-sm text-gray-500 mb-3">{team.description}</p>}
            <div className="flex flex-wrap gap-2">
              {team.members?.map((m) => (
                <div key={m.id} className="flex items-center space-x-1.5 bg-gray-50 border border-gray-200 rounded-full px-3 py-1">
                  <div className="w-5 h-5 bg-[#06AC38] rounded-full flex items-center justify-center">
                    <span className="text-white text-xs">{m.name?.[0]}</span>
                  </div>
                  <span className="text-xs text-gray-700">{m.name}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
        {teams.length === 0 && (
          <div className="col-span-2 text-center py-12 text-gray-400 bg-white rounded-xl border border-gray-100">
            No teams yet.
          </div>
        )}
      </div>

      {showCreate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg">
            <div className="px-6 py-4 border-b border-gray-100">
              <h2 className="text-lg font-semibold">Create Team</h2>
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
