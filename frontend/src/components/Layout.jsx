import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'
import {
  LayoutDashboard, AlertTriangle, Server, Calendar,
  Users, Shield, Bell, LogOut, Menu, X, ChevronDown
} from 'lucide-react'
import { useState } from 'react'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/incidents', icon: AlertTriangle, label: 'Incidents' },
  { to: '/alerts', icon: Bell, label: 'Alerts' },
  { to: '/services', icon: Server, label: 'Services' },
  { to: '/schedules', icon: Calendar, label: 'Schedules' },
  { to: '/teams', icon: Users, label: 'Teams' },
  { to: '/users', icon: Users, label: 'Users' },
  { to: '/escalation-policies', icon: Shield, label: 'Escalation Policies' },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen overflow-hidden bg-gray-100">
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-[#1C2A3A] transform transition-transform duration-200 ease-in-out lg:relative lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex items-center justify-between h-16 px-6 bg-[#152231]">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-[#06AC38] rounded flex items-center justify-center">
              <Bell size={16} className="text-white" />
            </div>
            <span className="text-white font-bold text-lg">PagerDuty</span>
          </div>
          <button onClick={() => setSidebarOpen(false)} className="lg:hidden text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        <nav className="mt-4 px-3 space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-[#06AC38] text-white'
                    : 'text-gray-300 hover:bg-[#2D3E50] hover:text-white'
                }`
              }
            >
              <Icon size={18} className="mr-3 flex-shrink-0" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-[#2D3E50]">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 min-w-0">
              <div className="w-8 h-8 bg-[#06AC38] rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-white text-xs font-bold">{user?.name?.[0]?.toUpperCase()}</span>
              </div>
              <div className="min-w-0">
                <p className="text-white text-sm font-medium truncate">{user?.name}</p>
                <p className="text-gray-400 text-xs truncate">{user?.role}</p>
              </div>
            </div>
            <button onClick={handleLogout} className="text-gray-400 hover:text-white ml-2">
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-white border-b border-gray-200 flex items-center px-4 lg:px-6">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden mr-4 text-gray-500 hover:text-gray-700"
          >
            <Menu size={20} />
          </button>
          <div className="flex-1" />
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500 hidden sm:block">{user?.email}</span>
          </div>
        </header>

        <main className="flex-1 overflow-auto p-4 lg:p-6">
          <Outlet />
        </main>
      </div>

      {sidebarOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}
    </div>
  )
}
