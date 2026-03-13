import { useEffect, useState } from 'react'
import { Plus, Edit2, Trash2, Battery } from 'lucide-react'
import { batteriesApi, equipmentApi } from '../services/api'

interface BatteryItem {
  id: number
  equipment_id: number
  serial_number: string
  capacity: number
  voltage_nominal: number
  install_date: string
  status: string
  created_at: string
  updated_at: string
  equipment_name?: string
}

interface Equipment {
  id: number
  name: string
}

const BatteriesPage = () => {
  const [batteries, setBatteries] = useState<BatteryItem[]>([])
  const [equipment, setEquipment] = useState<Equipment[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingItem, setEditingItem] = useState<BatteryItem | null>(null)
  const [formData, setFormData] = useState({
    equipment_id: 0,
    serial_number: '',
    capacity: '',
    voltage_nominal: '',
    install_date: '',
    status: 'active'
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [batteriesRes, equipmentRes] = await Promise.all([
        batteriesApi.getAll(),
        equipmentApi.getAll()
      ])
      setBatteries(batteriesRes.data)
      setEquipment(equipmentRes.data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching data:', error)
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const data = {
        ...formData,
        capacity: parseFloat(formData.capacity),
        voltage_nominal: parseFloat(formData.voltage_nominal),
        install_date: formData.install_date
      }
      if (editingItem) {
        await batteriesApi.update(editingItem.id, data)
      } else {
        await batteriesApi.create(data)
      }
      setShowForm(false)
      setEditingItem(null)
      setFormData({
        equipment_id: 0,
        serial_number: '',
        capacity: '',
        voltage_nominal: '',
        install_date: '',
        status: 'active'
      })
      fetchData()
    } catch (error) {
      console.error('Error saving battery:', error)
    }
  }

  const handleEdit = (item: BatteryItem) => {
    setEditingItem(item)
    setFormData({
      equipment_id: item.equipment_id,
      serial_number: item.serial_number,
      capacity: item.capacity.toString(),
      voltage_nominal: item.voltage_nominal.toString(),
      install_date: item.install_date,
      status: item.status
    })
    setShowForm(true)
  }

  const handleDelete = async (id: number) => {
    if (window.confirm('Видалити батарею?')) {
      try {
        await batteriesApi.delete(id)
        fetchData()
      } catch (error) {
        console.error('Error deleting battery:', error)
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
          <Battery className="w-6 h-6" />
          Батареї
        </h1>
        <button
          onClick={() => {
            setEditingItem(null)
            setFormData({
              equipment_id: equipment[0]?.id || 0,
              serial_number: '',
              capacity: '',
              voltage_nominal: '',
              install_date: new Date().toISOString().split('T')[0],
              status: 'active'
            })
            setShowForm(true)
          }}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-primary-700"
        >
          <Plus className="w-4 h-4" />
          Додати
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">
              {editingItem ? 'Редагувати' : 'Додати'} батарею
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Обладнання</label>
                <select
                  value={formData.equipment_id}
                  onChange={(e) => setFormData({ ...formData, equipment_id: parseInt(e.target.value) })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                >
                  <option value="0">Виберіть обладнання</option>
                  {equipment.map((eq) => (
                    <option key={eq.id} value={eq.id}>{eq.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Серійний номер</label>
                <input
                  type="text"
                  value={formData.serial_number}
                  onChange={(e) => setFormData({ ...formData, serial_number: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Ємність (Ah)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.capacity}
                  onChange={(e) => setFormData({ ...formData, capacity: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Номінальна напруга (V)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.voltage_nominal}
                  onChange={(e) => setFormData({ ...formData, voltage_nominal: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Дата встановлення</label>
                <input
                  type="date"
                  value={formData.install_date}
                  onChange={(e) => setFormData({ ...formData, install_date: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Статус</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="active">Активна</option>
                  <option value="inactive">Неактивна</option>
                  <option value="maintenance">Обслуговування</option>
                  <option value="decommissioned">Списана</option>
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Серійний номер</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Обладнання</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ємність</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Напруга</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Дата встановлення</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Статус</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Дії</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {batteries.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-900">{item.serial_number}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{item.equipment_name}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{item.capacity} Ah</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{item.voltage_nominal} V</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{item.install_date}</td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                      item.status === 'active' ? 'bg-green-100 text-green-800' :
                      item.status === 'maintenance' ? 'bg-yellow-100 text-yellow-800' :
                      item.status === 'decommissioned' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {item.status === 'active' ? 'Активна' :
                       item.status === 'maintenance' ? 'Обслуговування' :
                       item.status === 'decommissioned' ? 'Списана' : 'Неактивна'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleEdit(item)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(item.id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
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

export default BatteriesPage
