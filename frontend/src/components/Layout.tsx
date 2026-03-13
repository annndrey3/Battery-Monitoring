import { Outlet, Link, useLocation } from 'react-router-dom'
import { Battery, Settings, AlertTriangle, BarChart3, Zap, FileText, Menu, X } from 'lucide-react'
import { useState } from 'react'

const Layout = () => {
  const location = useLocation()
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const navItems = [
    { path: '/', label: 'Головна', icon: BarChart3 },
    { path: '/equipment', label: 'Обладнання', icon: Settings },
    { path: '/batteries', label: 'Батареї', icon: Battery },
    { path: '/measurements', label: 'Виміри', icon: Zap },
    { path: '/incidents', label: 'Інциденти', icon: AlertTriangle },
    { path: '/reports', label: 'Звіти', icon: FileText },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile Header */}
      <div className="lg:hidden bg-white shadow-sm p-4 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Battery className="w-6 h-6 text-primary-600" />
          <span className="font-bold text-lg">Моніторинг батарей</span>
        </div>
        <button onClick={() => setIsMenuOpen(!isMenuOpen)} className="p-2">
          {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="lg:hidden bg-white border-b shadow-sm">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setIsMenuOpen(false)}
                className={`flex items-center space-x-3 px-4 py-3 transition-colors ${
                  isActive 
                    ? 'bg-primary-50 text-primary-600 border-r-2 border-primary-600' 
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </div>
      )}

      <div className="flex">
        {/* Desktop Sidebar */}
        <div className="hidden lg:block w-64 bg-white shadow-sm min-h-screen fixed left-0 top-0">
          <div className="p-6">
            <div className="flex items-center space-x-2 mb-8">
              <Battery className="w-8 h-8 text-primary-600" />
              <span className="font-bold text-xl">Моніторинг батарей</span>
            </div>
            <nav className="space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                      isActive 
                        ? 'bg-primary-50 text-primary-600' 
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{item.label}</span>
                  </Link>
                )
              })}
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 lg:ml-64 p-4 lg:p-8">
          <Outlet />
        </div>
      </div>
    </div>
  )
}

export default Layout
