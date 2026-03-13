import { useEffect, useState } from 'react'
import { Plus, Check, AlertTriangle, X } from 'lucide-react'
import { incidentsApi, batteriesApi } from '../services/api'

interface Incident {
  id: number
  measurement_id?: number
  battery_id?: number
  incident_type: string
  description: string
  severity: string
  is_resolved: boolean
  resolved_at?: string
  resolved_by?: number
  created_at: string
  battery_serial?: string
  equipment_name?: string
}

interface Battery {
  id: number
  serial_number: string
}

const IncidentsPage = () => {
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [batteries, setBatteries] = useState<Battery[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [filter, setFilter] = useState<'all' | 'active' | 'resolved'>('all')
  const [formData, setFormData] = useState({
    battery_id: 0,
    incident_type: 'warning',
    description: '',
    severity: 'medium'
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [incidentsRes, batteriesRes] = await Promise.all([
        incidentsApi.getAll(),
        batteriesApi.getAll()
      ])
      setIncidents(incidentsRes.data)
      setBatteries(batteriesRes.data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching data:', error)
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await incidentsApi.create(formData)
      setShowForm(false)
      setFormData({
        battery_id: batteries[0]?.id || 0,
        incident_type: 'warning',
        description: '',
        severity: 'medium'
      })
      fetchData()
    } catch (error) {
      console.error('Error creating incident:', error)
    }
  }

  const handleResolve = async (id: number) => {
    try {
      await incidentsApi.update(id, { is_resolved: true })
      fetchData()
    } catch (error) {
      console.error('Error resolving incident:', error)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-blue-100 text-blue-800'
    }
  }

  const getIncidentTypeLabel = (type: string) => {
    const labels: { [key: string]: string } = {
      overheat: 'Перегрів',
      low_charge: 'Низький заряд',
      voltage_spike: 'Стрибок напруги',
      current_surge: 'Стрибок струму',
      critical_failure: 'Критичний збій',
      warning: 'Попередження'
    }
    return labels[type] || type
  }

  const filteredIncidents = incidents.filter(incident => {
    if (filter === 'active') return !incident.is_resolved
    if (filter === 'resolved') return incident.is_resolved
    return true
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <AlertTriangle className="w-6 h-6" />
          Інциденти
        </h1>
        <button
          onClick={() => {
            setFormData({
              battery_id: batteries[0]?.id || 0,
              incident_type: 'warning',
              description: '',
              severity: 'medium'
            })
            setShowForm(true)
          }}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-primary-700"
        >
          <Plus className="w-4 h-4" />
          Додати
        </button>
      </div>

      {/* Filter */}
      <div className="flex gap-2">
        {(['all', 'active', 'resolved'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg ${
              filter === f 
                ? 'bg-primary-600 text-white' 
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            {f === 'all' ? 'Всі' : f === 'active' ? 'Активні' : 'Вирішені'}
          </button>
        ))}
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Додати інцидент</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Батарея</label>
                <select
                  value={formData.battery_id}
                  onChange={(e) => setFormData({ ...formData, battery_id: parseInt(e.target.value) })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                >
                  <option value="0">Виберіть батарею</option>
                  {batteries.map((b) => (
                    <option key={b.id} value={b.id}>{b.serial_number}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Тип інциденту</label>
                <select
                  value={formData.incident_type}
                  onChange={(e) => setFormData({ ...formData, incident_type: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="overheat">Перегрів</option>
                  <option value="low_charge">Низький заряд</option>
                  <option value="voltage_spike">Стрибок напруги</option>
                  <option value="current_surge">Стрибок струму</option>
                  <option value="critical_failure">Критичний збій</option>
                  <option value="warning">Попередження</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Опис</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  rows={3}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Серйозність</label>
                <select
                  value={formData.severity}
                  onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="low">Низька</option>
                  <option value="medium">Середня</option>
                  <option value="high">Висока</option>
                  <option value="critical">Критична</option>
                </select>
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  className="flex-1 bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700"
                >
                  Зберегти
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400"
                >
                  Скасувати
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Батарея</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Тип</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Опис</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Серйозність</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Статус</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Створено</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Дії</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredIncidents.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {item.battery_serial}
                    <div className="text-xs text-gray-500">{item.equipment_name}</div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {getIncidentTypeLabel(item.incident_type)}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                    {item.description}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`inline-flex px-2 py-1 text-xs rounded-full ${getSeverityColor(item.severity)}`}>
                      {item.severity === 'critical' ? 'Критична' :
                       item.severity === 'high' ? 'Висока' :
                       item.severity === 'medium' ? 'Середня' : 'Низька'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                      item.is_resolved ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {item.is_resolved ? (
                        <><Check className="w-3 h-3 mr-1" /> Вирішено</>
                      ) : (
                        <><X className="w-3 h-3 mr-1" /> Активний</>
                      )}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(item.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {!item.is_resolved && (
                      <button
                        onClick={() => handleResolve(item.id)}
                        className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                      >
                        Вирішити
                      </button>
                    )}
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

export default IncidentsPage
