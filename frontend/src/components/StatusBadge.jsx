export default function StatusBadge({ status, size = 'sm' }) {
  const classes = {
    triggered: 'bg-red-100 text-red-800 border border-red-200',
    acknowledged: 'bg-yellow-100 text-yellow-800 border border-yellow-200',
    resolved: 'bg-green-100 text-green-800 border border-green-200',
    active: 'bg-green-100 text-green-800 border border-green-200',
    warning: 'bg-yellow-100 text-yellow-800 border border-yellow-200',
    critical: 'bg-red-100 text-red-800 border border-red-200',
    maintenance: 'bg-blue-100 text-blue-800 border border-blue-200',
  }
  const sizeClass = size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-sm px-3 py-1'
  return (
    <span className={`inline-flex items-center rounded-full font-medium ${sizeClass} ${classes[status] || 'bg-gray-100 text-gray-800'}`}>
      {status}
    </span>
  )
}
