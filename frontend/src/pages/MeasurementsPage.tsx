import { useEffect, useState } from 'react'
import { Plus, Trash2, Zap } from 'lucide-react'
import { measurementsApi, batteriesApi } from '../services/api'

interface Measurement {
  id: number
  battery_id: number
  voltage: number
  current: number
  charge_level: number
  temperature: number
  timestamp: string
  operator_name?: string
  battery_serial?: string
}

interface Battery {
  id: number
  serial_number: string
}

const MeasurementsPage = () => {
  const [measurements, setMeasurements] = useState<Measurement[]>([])
  const [batteries, setBatteries] = useState<Battery[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    battery_id: 0,
    voltage: '',
    current: '',
    charge_level: '',
    temperature: ''
  })
  const [errors, setErrors] = useState<string[]>([])

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [measurementsRes, batteriesRes] = await Promise.all([
        measurementsApi.getAll(),
        batteriesApi.getAll()
      ])
      setMeasurements(measurementsRes.data)
      setBatteries(batteriesRes.data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching data:', error)
      setLoading(false)
    }
  }

  const validateForm = () => {
    const errs: string[] = []
    const voltage = parseFloat(formData.voltage)
    const current = parseFloat(formData.current)
    const charge = parseFloat(formData.charge_level)
    const temp = parseFloat(formData.temperature)

    if (voltage <= 0) errs.push('Напруга повинна бути більше 0')
    if (current < 0) errs.push('Струм не може бути від\'ємним')
    if (charge < 0 || charge > 100) errs.push('Рівень заряду повинен бути від 0 до 100%')
    if (temp > 80) errs.push('Температура не повинна перевищувати 80°C')

    setErrors(errs)
    return errs.length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validateForm()) return

    try {
      const data = {
        battery_id: formData.battery_id,
        voltage: parseFloat(formData.voltage),
        current: parseFloat(formData.current),
        charge_level: parseFloat(formData.charge_level),
        temperature: parseFloat(formData.temperature)
        // measured_by убран - нет авторизации
      }
      await measurementsApi.create(data)
      setShowForm(false)
      setFormData({
        battery_id: batteries[0]?.id || 0,
        voltage: '',
        current: '',
        charge_level: '',
        temperature: ''
      })
      setErrors([])
      fetchData()
    } catch (error) {
      console.error('Error saving measurement:', error)
    }
  }

  const handleDelete = async (id: number) => {
    if (window.confirm('Видалити вимір?')) {
      try {
        await measurementsApi.delete(id)
        fetchData()
      } catch (error) {
        console.error('Error deleting measurement:', error)
      }
    }
  }

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
          <Zap className="w-6 h-6" />
          Виміри
        </h1>
        <button
          onClick={() => {
            setFormData({
              battery_id: batteries[0]?.id || 0,
              voltage: '',
              current: '',
              charge_level: '',
              temperature: ''
            })
            setErrors([])
            setShowForm(true)
          }}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-primary-700"
        >
          <Plus className="w-4 h-4" />
          Додати вимір
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Додати вимір</h2>
            {errors.length > 0 && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
                {errors.map((err, i) => (
                  <div key={i}>{err}</div>
                ))}
              </div>
            )}
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
                <label className="block text-sm font-medium text-gray-700">Напруга (V)</label>
                <input
                  type="number"
                  step="0.001"
                  value={formData.voltage}
                  onChange={(e) => setFormData({ ...formData, voltage: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Струм (A)</label>
                <input
                  type="number"
                  step="0.001"
                  value={formData.current}
                  onChange={(e) => setFormData({ ...formData, current: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Рівень заряду (%)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="100"
                  value={formData.charge_level}
                  onChange={(e) => setFormData({ ...formData, charge_level: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Температура (°C)</label>
                <input
                  type="number"
                  step="0.01"
                  max="80"
                  value={formData.temperature}
                  onChange={(e) => setFormData({ ...formData, temperature: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Напруга</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Струм</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Заряд</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Температура</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Час</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Дії</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {measurements.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-900">{item.battery_serial}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{item.voltage} V</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{item.current} A</td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                      item.charge_level < 20 ? 'bg-red-100 text-red-800' : 
                      item.charge_level < 50 ? 'bg-yellow-100 text-yellow-800' : 
                      'bg-green-100 text-green-800'
                    }`}>
                      {item.charge_level}%
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                      item.temperature > 60 ? 'bg-red-100 text-red-800' : 
                      item.temperature > 40 ? 'bg-yellow-100 text-yellow-800' : 
                      'bg-green-100 text-green-800'
                    }`}>
                      {item.temperature}°C
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(item.timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
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

export default MeasurementsPage
