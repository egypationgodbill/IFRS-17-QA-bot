import { useState, useEffect } from 'react'
import { Plus, Shield, ChevronRight } from 'lucide-react'
import api from '../api'

export default function EscalationPolicies() {
  const [policies, setPolicies] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [users, setUsers] = useState([])
  const [form, setForm] = useState({ name: '', description: '', repeat_enabled: false, num_loops: 0 })
  const [rules, setRules] = useState([{ escalation_delay_in_minutes: 30, target_user_ids: [] }])

  useEffect(() => {
    Promise.all([api.get('/escalation-policies'), api.get('/users')]).then(([p, u]) => {
      setPolicies(p.data)
      setUsers(u.data)
    }).finally(() => setLoading(false))
  }, [])

  const addRule = () => setRules([...rules, { escalation_delay_in_minutes: 30, target_user_ids: [] }])

  const updateRule = (i, field, value) => {
    const updated = [...rules]
    updated[i] = { ...updated[i], [field]: value }
    setRules(updated)
  }

  const toggleUser = (ruleIdx, uid) => {
    const rule = rules[ruleIdx]
    const ids = rule.target_user_ids.includes(uid)
      ? rule.target_user_ids.filter((id) => id !== uid)
      : [...rule.target_user_ids, uid]
    updateRule(ruleIdx, 'target_user_ids', ids)
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    const payload = { ...form, rules }
    const res = await api.post('/escalation-policies', payload)
    setPolicies([...policies, res.data])
    setShowCreate(false)
    setForm({ name: '', description: '', repeat_enabled: false, num_loops: 0 })
    setRules([{ escalation_delay_in_minutes: 30, target_user_ids: [] }])
  }

  if (loading) return <div className="text-center py-12 text-gray-400">Loading…</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Escalation Policies</h1>
          <p className="text-gray-500 text-sm mt-1">{policies.length} policies</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center space-x-2 bg-[#06AC38] hover:bg-[#058A2E] text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          <Plus size={16} />
          <span>New Policy</span>
        </button>
      </div>

      <div className="space-y-4">
        {policies.map((policy) => (
          <div key={policy.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-orange-50 rounded-lg flex items-center justify-center">
                <Shield size={18} className="text-orange-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{policy.name}</h3>
                {policy.description && <p className="text-sm text-gray-500">{policy.description}</p>}
              </div>
            </div>
            <div className="space-y-2">
              {policy.rules?.map((rule, i) => (
                <div key={rule.id} className="flex items-center space-x-3 text-sm">
                  <span className="flex-shrink-0 w-6 h-6 bg-gray-100 rounded-full flex items-center justify-center text-xs font-medium text-gray-600">
                    {i + 1}
                  </span>
                  <div className="flex items-center space-x-2 flex-1">
                    <span className="text-gray-500">Notify</span>
                    <div className="flex flex-wrap gap-1">
                      {rule.targets?.map((u) => (
                        <span key={u.id} className="bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full text-xs">{u.name}</span>
                      ))}
                      {!rule.targets?.length && <span className="text-gray-400 italic">no targets</span>}
                    </div>
                  </div>
                  {i < policy.rules.length - 1 && (
                    <span className="text-gray-400 text-xs">then escalate after {rule.escalation_delay_in_minutes}m</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
        {policies.length === 0 && (
          <div className="text-center py-12 text-gray-400 bg-white rounded-xl border border-gray-100">No escalation policies yet.</div>
        )}
      </div>

      {showCreate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-auto">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl my-8">
            <div className="px-6 py-4 border-b border-gray-100">
              <h2 className="text-lg font-semibold">Create Escalation Policy</h2>
            </div>
            <form onSubmit={handleCreate} className="p-6 space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                  <input className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
                    value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <input className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
                    value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-gray-900">Escalation Rules</h3>
                  <button type="button" onClick={addRule} className="text-sm text-[#06AC38] hover:underline">+ Add Rule</button>
                </div>
                <div className="space-y-4">
                  {rules.map((rule, i) => (
                    <div key={i} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center space-x-2 mb-3">
                        <span className="w-6 h-6 bg-[#06AC38] rounded-full flex items-center justify-center text-white text-xs">{i + 1}</span>
                        <span className="font-medium text-sm text-gray-700">Rule {i + 1}</span>
                      </div>
                      <div className="mb-3">
                        <label className="block text-xs font-medium text-gray-500 mb-1">Delay (minutes)</label>
                        <input type="number" min="0" className="w-32 border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
                          value={rule.escalation_delay_in_minutes}
                          onChange={(e) => updateRule(i, 'escalation_delay_in_minutes', parseInt(e.target.value))} />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-500 mb-2">Notify Users</label>
                        <div className="flex flex-wrap gap-2">
                          {users.map((u) => (
                            <button
                              key={u.id}
                              type="button"
                              onClick={() => toggleUser(i, u.id)}
                              className={`px-3 py-1 rounded-full text-xs border transition-colors ${
                                rule.target_user_ids.includes(u.id)
                                  ? 'bg-[#06AC38] border-[#06AC38] text-white'
                                  : 'border-gray-300 text-gray-600 hover:border-[#06AC38]'
                              }`}
                            >
                              {u.name}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <input type="checkbox" id="repeat" checked={form.repeat_enabled}
                  onChange={(e) => setForm({ ...form, repeat_enabled: e.target.checked })} className="rounded" />
                <label htmlFor="repeat" className="text-sm text-gray-700">Repeat policy if no response</label>
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
