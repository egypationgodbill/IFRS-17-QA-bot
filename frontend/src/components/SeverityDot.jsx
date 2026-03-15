const colors = {
  critical: 'bg-red-500',
  high: 'bg-orange-500',
  warning: 'bg-yellow-500',
  info: 'bg-blue-500',
}

export default function SeverityDot({ severity }) {
  return (
    <span className={`inline-block w-2.5 h-2.5 rounded-full ${colors[severity] || 'bg-gray-400'}`} title={severity} />
  )
}
