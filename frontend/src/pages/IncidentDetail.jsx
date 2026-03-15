import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, CheckCircle, XCircle, Clock, MessageSquare, AlertTriangle } from 'lucide-react'
import api from '../api'
import StatusBadge from '../components/StatusBadge'
import SeverityDot from '../components/SeverityDot'
import { format, formatDistanceToNow } from 'date-fns'

const TIMELINE_ICONS = {
  triggered: <AlertTriangle size={14} className="text-red-500" />,
  acknowledged: <Clock size={14} className="text-yellow-500" />,
  resolved: <CheckCircle size={14} className="text-green-500" />,
  note_added: <MessageSquare size={14} className="text-blue-500" />,
  escalated: <AlertTriangle size={14} className="text-orange-500" />,
}

export default function IncidentDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [incident, setIncident] = useState(null)
  const [loading, setLoading] = useState(true)
  const [note, setNote] = useState('')
  const [posting, setPosting] = useState(false)

  const fetch = () => {
    api.get(`/incidents/${id}`).then((res) => {
      setIncident(res.data)
      setLoading(false)
    })
  }

  useEffect(() => { fetch() }, [id])

  const acknowledge = async () => {
    await api.post(`/incidents/${id}/acknowledge`)
    fetch()
  }

  const resolve = async () => {
    await api.post(`/incidents/${id}/resolve`)
    fetch()
  }

  const addNote = async (e) => {
    e.preventDefault()
    if (!note.trim()) return
    setPosting(true)
    await api.post(`/incidents/${id}/notes`, { content: note })
    setNote('')
    setPosting(false)
    fetch()
  }

  if (loading) return <div className="text-center py-12 text-gray-400">Loading…</div>
  if (!incident) return <div className="text-center py-12 text-gray-400">Not found</div>

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center space-x-3">
        <button onClick={() => navigate('/incidents')} className="text-gray-400 hover:text-gray-600">
          <ArrowLeft size={20} />
        </button>
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <SeverityDot severity={incident.severity} />
            <h1 className="text-xl font-bold text-gray-900">
              #{incident.incident_number} — {incident.title}
            </h1>
          </div>
          <p className="text-gray-500 text-sm mt-0.5">
            {incident.service?.name} · Created {formatDistanceToNow(new Date(incident.created_at), { addSuffix: true })}
          </p>
        </div>
        <StatusBadge status={incident.status} size="md" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Actions */}
          {incident.status !== 'resolved' && (
            <div className="flex space-x-3">
              {incident.status === 'triggered' && (
                <button
                  onClick={acknowledge}
                  className="flex items-center space-x-2 px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white rounded-lg text-sm font-medium transition-colors"
                >
                  <Clock size={16} />
                  <span>Acknowledge</span>
                </button>
              )}
              <button
                onClick={resolve}
                className="flex items-center space-x-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg text-sm font-medium transition-colors"
              >
                <CheckCircle size={16} />
                <span>Resolve</span>
              </button>
            </div>
          )}

          {/* Description */}
          {incident.description && (
            <div className="bg-white rounded-xl border border-gray-100 p-6">
              <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
              <p className="text-gray-600 text-sm whitespace-pre-line">{incident.description}</p>
            </div>
          )}

          {/* Notes */}
          <div className="bg-white rounded-xl border border-gray-100 p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Notes</h3>
            {incident.notes?.length === 0 && (
              <p className="text-gray-400 text-sm mb-4">No notes yet.</p>
            )}
            <div className="space-y-3 mb-4">
              {incident.notes?.map((note) => (
                <div key={note.id} className="flex space-x-3">
                  <div className="w-8 h-8 bg-[#06AC38] rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-white text-xs">{note.user?.name?.[0]}</span>
                  </div>
                  <div className="flex-1 bg-gray-50 rounded-lg px-4 py-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-900">{note.user?.name}</span>
                      <span className="text-xs text-gray-400">{formatDistanceToNow(new Date(note.created_at), { addSuffix: true })}</span>
                    </div>
                    <p className="text-sm text-gray-700">{note.content}</p>
                  </div>
                </div>
              ))}
            </div>
            <form onSubmit={addNote} className="flex space-x-2">
              <input
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Add a note…"
                className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#06AC38]"
              />
              <button
                type="submit"
                disabled={posting}
                className="px-4 py-2 bg-[#06AC38] hover:bg-[#058A2E] text-white rounded-lg text-sm font-medium disabled:opacity-50"
              >
                Add
              </button>
            </form>
          </div>

          {/* Timeline */}
          <div className="bg-white rounded-xl border border-gray-100 p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Timeline</h3>
            <div className="space-y-4">
              {incident.timeline?.map((entry) => (
                <div key={entry.id} className="flex items-start space-x-3">
                  <div className="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    {TIMELINE_ICONS[entry.type] || <AlertTriangle size={12} />}
                  </div>
                  <div>
                    <p className="text-sm text-gray-700">{entry.summary}</p>
                    <p className="text-xs text-gray-400">{format(new Date(entry.created_at), 'MMM d, yyyy HH:mm')}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Side panel */}
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-gray-100 p-5">
            <h3 className="font-semibold text-gray-900 mb-3 text-sm">Details</h3>
            <dl className="space-y-3 text-sm">
              <div>
                <dt className="text-gray-500">Status</dt>
                <dd className="mt-0.5"><StatusBadge status={incident.status} /></dd>
              </div>
              <div>
                <dt className="text-gray-500">Severity</dt>
                <dd className="mt-0.5 flex items-center space-x-1.5">
                  <SeverityDot severity={incident.severity} />
                  <span className="capitalize">{incident.severity}</span>
                </dd>
              </div>
              <div>
                <dt className="text-gray-500">Service</dt>
                <dd className="mt-0.5 font-medium">{incident.service?.name}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Assigned To</dt>
                <dd className="mt-0.5">{incident.assigned_to?.name || 'Unassigned'}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Created By</dt>
                <dd className="mt-0.5">{incident.created_by?.name || '—'}</dd>
              </div>
              {incident.acknowledged_at && (
                <div>
                  <dt className="text-gray-500">Acknowledged</dt>
                  <dd className="mt-0.5">{format(new Date(incident.acknowledged_at), 'MMM d HH:mm')}</dd>
                </div>
              )}
              {incident.resolved_at && (
                <div>
                  <dt className="text-gray-500">Resolved</dt>
                  <dd className="mt-0.5">{format(new Date(incident.resolved_at), 'MMM d HH:mm')}</dd>
                </div>
              )}
            </dl>
          </div>

          {incident.responders?.length > 0 && (
            <div className="bg-white rounded-xl border border-gray-100 p-5">
              <h3 className="font-semibold text-gray-900 mb-3 text-sm">Responders</h3>
              <div className="space-y-2">
                {incident.responders.map((u) => (
                  <div key={u.id} className="flex items-center space-x-2">
                    <div className="w-7 h-7 bg-[#06AC38] rounded-full flex items-center justify-center">
                      <span className="text-white text-xs">{u.name?.[0]}</span>
                    </div>
                    <span className="text-sm text-gray-700">{u.name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
