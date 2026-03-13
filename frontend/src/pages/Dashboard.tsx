import { useEffect, useState } from 'react'
import { Battery, AlertTriangle, Activity, Settings } from 'lucide-react'
import { equipmentApi, batteriesApi, measurementsApi, incidentsApi } from '../services/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface Stats {
  equipment: number
  batteries: number
  measurements: number
  activeIncidents: number
}

interface RecentMeasurement {
  id: number
  battery_serial: string
  voltage: number
  charge_level: number
  temperature: number
  timestamp: string
}

const Dashboard = () => {
  const [stats, setStats] = useState<Stats>({ equipment: 0, batteries: 0, measurements: 0, activeIncidents: 0 })
  const [recentMeasurements, setRecentMeasurements] = useState<RecentMeasurement[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [equipmentRes, batteriesRes, measurementsRes, incidentsRes] = await Promise.all([
          equipmentApi.getAll(),
          batteriesApi.getAll(),
          measurementsApi.getAll({ limit: 10 }),
          incidentsApi.getAll({ is_resolved: false }),
        ])

        setStats({
          equipment: equipmentRes.data.length,
          batteries: batteriesRes.data.length,
          measurements: measurementsRes.data.length,
          activeIncidents: incidentsRes.data.length,
        })

        setRecentMeasurements(measurementsRes.data.slice(0, 10))
        setLoading(false)
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const chartData = recentMeasurements.map(m => ({
    time: new Date(m.timestamp).toLocaleTimeString(),
    charge: Number(m.charge_level),
    voltage: Number(m.voltage),
    temp: Number(m.temperature),
  })).reverse()

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Головна панель</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Обладнання</p>
              <p className="text-2xl font-bold text-gray-900">{stats.equipment}</p>
            </div>
            <Settings className="w-8 h-8 text-primary-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Батареї</p>
              <p className="text-2xl font-bold text-gray-900">{stats.batteries}</p>
            </div>
            <Battery className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Виміри</p>
              <p className="text-2xl font-bold text-gray-900">{stats.measurements}</p>
            </div>
            <Activity className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Активні інциденти</p>
              <p className="text-2xl font-bold text-red-600">{stats.activeIncidents}</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-red-500" />
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Останні виміри</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="charge" stroke="#3b82f6" name="Заряд %" />
              <Line type="monotone" dataKey="voltage" stroke="#10b981" name="Напруга V" />
              <Line type="monotone" dataKey="temp" stroke="#f59e0b" name="Температура °C" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Measurements Table */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <div className="p-6 border-b">
          <h2 className="text-lg font-semibold">Останні виміри</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Батарея</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Напруга</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Заряд</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Температура</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Час</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {recentMeasurements.map((m) => (
                <tr key={m.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-900">{m.battery_serial}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{m.voltage} V</td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                      m.charge_level < 20 ? 'bg-red-100 text-red-800' : 
                      m.charge_level < 50 ? 'bg-yellow-100 text-yellow-800' : 
                      'bg-green-100 text-green-800'
                    }`}>
                      {m.charge_level}%
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                      m.temperature > 60 ? 'bg-red-100 text-red-800' : 
                      m.temperature > 40 ? 'bg-yellow-100 text-yellow-800' : 
                      'bg-green-100 text-green-800'
                    }`}>
                      {m.temperature}°C
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(m.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
