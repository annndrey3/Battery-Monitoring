import { useEffect, useState } from 'react'
import { FileText, Download, BarChart3, Thermometer, Zap, AlertTriangle, Brain, RefreshCw } from 'lucide-react'
import { reportsApi, batteriesApi } from '../services/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area } from 'recharts'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

const ReportsPage = () => {
  const [activeTab, setActiveTab] = useState('charge')
  const [batteries, setBatteries] = useState<{ id: number; serial_number: string }[]>([])
  const [selectedBattery, setSelectedBattery] = useState<number>(0)
  const [loading, setLoading] = useState(false)
  
  // Report data
  const [chargeData, setChargeData] = useState<any[]>([])
  const [tempAlerts, setTempAlerts] = useState<any[]>([])
  const [voltageData, setVoltageData] = useState<any[]>([])
  const [incidentStats, setIncidentStats] = useState<any[]>([])
  const [dischargeData, setDischargeData] = useState<any[]>([])
  const [tempChartData, setTempChartData] = useState<any[]>([])
  const [aiAnalysisData, setAiAnalysisData] = useState<any>(null)
  const [aiLoading, setAiLoading] = useState(false)

  useEffect(() => {
    fetchBatteries()
    fetchReports()
  }, [])

  useEffect(() => {
    if (selectedBattery > 0) {
      fetchBatteryCharts(selectedBattery)
    }
  }, [selectedBattery])

  const fetchBatteries = async () => {
    try {
      const response = await batteriesApi.getAll()
      setBatteries(response.data)
      if (response.data.length > 0) {
        setSelectedBattery(response.data[0].id)
      }
    } catch (error) {
      console.error('Error fetching batteries:', error)
    }
  }

  const fetchReports = async () => {
    setLoading(true)
    try {
      const [chargeRes, tempRes, voltageRes, incidentRes, aiRes] = await Promise.all([
        reportsApi.getChargeLevels(),
        reportsApi.getTemperatureAlerts(),
        reportsApi.getVoltageDeviation(),
        reportsApi.getIncidentStats(),
        reportsApi.getAIAnalysis()
      ])
      setChargeData(chargeRes.data)
      setTempAlerts(tempRes.data)
      setVoltageData(voltageRes.data)
      setIncidentStats(incidentRes.data)
      setAiAnalysisData(aiRes.data)
    } catch (error) {
      console.error('Error fetching reports:', error)
    }
    setLoading(false)
  }

  const fetchAIAnalysis = async () => {
    setAiLoading(true)
    try {
      const response = await reportsApi.getAIAnalysis()
      setAiAnalysisData(response.data)
    } catch (error) {
      console.error('Error fetching AI analysis:', error)
    }
    setAiLoading(false)
  }

  const fetchBatteryCharts = async (batteryId: number) => {
    try {
      const [dischargeRes, tempRes] = await Promise.all([
        reportsApi.getBatteryDischarge(batteryId, 7),
        reportsApi.getTemperatureChart(batteryId, 7)
      ])
      setDischargeData(dischargeRes.data.data || [])
      setTempChartData(tempRes.data.data || [])
    } catch (error) {
      console.error('Error fetching battery charts:', error)
    }
  }

  const translateAlertLevel = (level: string) => {
    const upperLevel = level?.toUpperCase() || ''
    const levels: { [key: string]: string } = {
      'КРИТИЧЕСКАЯ': 'КРИТИЧНА',
      'ВЫСОКАЯ': 'ВИСОКА',
      'СРЕДНЯЯ': 'СЕРЕДНЯ',
      'НИЗКАЯ': 'НИЗЬКА'
    }
    return levels[upperLevel] || level
  }

  const translateStatus = (status: string) => {
    const statuses: { [key: string]: string } = {
      'НОРМА': 'НОРМА',
      'ВНИМАНИЕ': 'УВАГА',
      'КРИТИЧЕСКАЯ': 'КРИТИЧНО',
      'АВАРИЯ': 'АВАРІЯ'
    }
    return statuses[status] || status
  }

  const tabs = [
    { id: 'charge', label: 'Рівень заряду', icon: Zap },
    { id: 'temperature', label: 'Температура', icon: Thermometer },
    { id: 'voltage', label: 'Напруга', icon: BarChart3 },
    { id: 'incidents', label: 'Інциденти', icon: AlertTriangle },
    { id: 'charts', label: 'Графіки батареї', icon: FileText },
    { id: 'ai', label: 'AI Аналіз', icon: Brain },
  ]

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
          <FileText className="w-6 h-6" />
          Звіти
        </h1>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
                activeTab === tab.id
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          )
        })}
      </div>

      {/* Charge Report */}
      {activeTab === 'charge' && (
        <div className="space-y-4">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-lg font-semibold mb-4">Середній рівень заряду за обладнанням</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chargeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="equipment_name" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Bar dataKey="avg_charge_level" fill="#3b82f6" name="Середній заряд %" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Обладнання</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Батареї</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Середній заряд</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Мін/Макс</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {chargeData.map((item, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-900">{item.equipment_name}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">{item.battery_count}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-500 h-2 rounded-full"
                            style={{ width: `${item.avg_charge_level}%` }}
                          />
                        </div>
                        {item.avg_charge_level}%
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {item.min_charge_level}% / {item.max_charge_level}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Temperature Alerts */}
      {activeTab === 'temperature' && (
        <div className="space-y-4">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-lg font-semibold mb-4">Критичні температури (&gt;60°C)</h2>
            {tempAlerts.length === 0 ? (
              <p className="text-gray-500">Немає критичних температур</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Батарея</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Обладнання</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Температура</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Заряд</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Рівень</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {tempAlerts.map((item, i) => (
                      <tr key={i} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm text-gray-900">{item.serial_number}</td>
                        <td className="px-6 py-4 text-sm text-gray-500">{item.equipment_name}</td>
                        <td className="px-6 py-4 text-sm text-red-600 font-semibold">{item.temperature}°C</td>
                        <td className="px-6 py-4 text-sm text-gray-900">{item.charge_level}%</td>
                        <td className="px-6 py-4 text-sm">
                          <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                            item.alert_level === 'КРИТИЧЕСКАЯ' ? 'bg-red-100 text-red-800' : 'bg-orange-100 text-orange-800'
                          }`}>
                            {translateAlertLevel(item.alert_level)}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Voltage Report */}
      {activeTab === 'voltage' && (
        <div className="space-y-4">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-lg font-semibold mb-4">Відхилення напруги від номіналу</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Батарея</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Номінальна</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Середня</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Відхилення</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Статус</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {voltageData.map((item, i) => (
                    <tr key={i} className="hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm text-gray-900">{item.serial_number}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">{item.voltage_nominal} V</td>
                      <td className="px-6 py-4 text-sm text-gray-900">{item.avg_voltage} V</td>
                      <td className="px-6 py-4 text-sm text-gray-900">{item.deviation_percent}%</td>
                      <td className="px-6 py-4 text-sm">
                        <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                          item.status === 'НОРМА' ? 'bg-green-100 text-green-800' :
                          item.status === 'ВНИМАНИЕ' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {translateStatus(item.status)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Incident Stats */}
      {activeTab === 'incidents' && (
        <div className="space-y-4">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-lg font-semibold mb-4">Статистика інцидентів</h2>
            {incidentStats.length === 0 ? (
              <p className="text-gray-500">Немає даних</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Тип</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Місяць</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Кількість</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Вирішено</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Критичні</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {incidentStats.map((item, i) => (
                      <tr key={i} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm text-gray-900">{item.incident_type}</td>
                        <td className="px-6 py-4 text-sm text-gray-500">{item.month}</td>
                        <td className="px-6 py-4 text-sm text-gray-900">{item.incident_count}</td>
                        <td className="px-6 py-4 text-sm text-green-600">{item.resolved_count}</td>
                        <td className="px-6 py-4 text-sm text-red-600">{item.critical_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Battery Charts */}
      {activeTab === 'charts' && (
        <div className="space-y-4">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <label className="block text-sm font-medium text-gray-700 mb-2">Виберіть батарею</label>
            <select
              value={selectedBattery}
              onChange={(e) => setSelectedBattery(parseInt(e.target.value))}
              className="block w-full max-w-xs border border-gray-300 rounded-md px-3 py-2"
            >
              {batteries.map((b) => (
                <option key={b.id} value={b.id}>{b.serial_number}</option>
              ))}
            </select>
          </div>

          {selectedBattery > 0 && (
            <>
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <h2 className="text-lg font-semibold mb-4">Графік розряду батареї (7 днів)</h2>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={dischargeData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="timestamp" tickFormatter={(val) => new Date(val).toLocaleDateString()} />
                      <YAxis yAxisId="left" domain={[0, 100]} />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip />
                      <Line yAxisId="left" type="monotone" dataKey="charge_level" stroke="#3b82f6" name="Заряд %" />
                      <Line yAxisId="right" type="monotone" dataKey="voltage" stroke="#10b981" name="Напруга V" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm">
                <h2 className="text-lg font-semibold mb-4">Температурний графік (7 днів)</h2>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={tempChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="hour" tickFormatter={(val) => val ? new Date(val).toLocaleDateString() : ''} />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="avg_temp" stroke="#f59e0b" name="Середня °C" />
                      <Line type="monotone" dataKey="max_temp" stroke="#ef4444" name="Макс °C" />
                      <Line type="monotone" dataKey="min_temp" stroke="#3b82f6" name="Мін °C" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* AI Analysis */}
      {activeTab === 'ai' && (
        <div className="space-y-6">
          {/* Health Score Card */}
          {aiAnalysisData?.stats && (
            <div className="bg-gradient-to-r from-primary-600 to-primary-700 p-6 rounded-lg shadow-sm text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold mb-1">AI Health Score</h2>
                  <p className="text-primary-100">Загальний стан системи батарей</p>
                </div>
                <div className="text-right">
                  <div className="text-5xl font-bold">{aiAnalysisData.stats.health_score}</div>
                  <div className="text-sm text-primary-100">з 100</div>
                </div>
              </div>
              <div className="mt-4 grid grid-cols-4 gap-4 text-sm">
                <div className="bg-white/10 rounded p-3">
                  <div className="text-primary-100">Батарей</div>
                  <div className="text-xl font-semibold">{aiAnalysisData.stats.total_batteries}</div>
                </div>
                <div className="bg-white/10 rounded p-3">
                  <div className="text-primary-100">Обладнання</div>
                  <div className="text-xl font-semibold">{aiAnalysisData.stats.total_equipment}</div>
                </div>
                <div className="bg-white/10 rounded p-3">
                  <div className="text-primary-100">Середній заряд</div>
                  <div className="text-xl font-semibold">{aiAnalysisData.stats.avg_charge}%</div>
                </div>
                <div className="bg-white/10 rounded p-3">
                  <div className="text-primary-100">Температура</div>
                  <div className="text-xl font-semibold">{aiAnalysisData.stats.avg_temp}°C</div>
                </div>
              </div>
            </div>
          )}

          {/* Recommendations */}
          {aiAnalysisData?.recommendations && (
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold flex items-center gap-2">
                  <Brain className="w-5 h-5 text-primary-600" />
                  AI Рекомендації
                  {aiAnalysisData?.ai_analysis === false && (
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">Локальний аналіз</span>
                  )}
                </h2>
                <button
                  onClick={fetchAIAnalysis}
                  disabled={aiLoading}
                  className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <RefreshCw className={`w-4 h-4 ${aiLoading ? 'animate-spin' : ''}`} />
                  {aiLoading ? 'Оновлення...' : 'Оновити'}
                </button>
              </div>
              <div className="space-y-3">
                {aiAnalysisData.recommendations.map((rec: string, i: number) => (
                  <div key={i} className={`p-4 rounded-lg flex items-start gap-3 ${
                    rec.includes('Увага') || rec.includes('критичн') || rec.includes('Висока') 
                      ? 'bg-red-50 border border-red-200 text-red-800' 
                      : rec.includes('нормальному') 
                        ? 'bg-green-50 border border-green-200 text-green-800'
                        : 'bg-yellow-50 border border-yellow-200 text-yellow-800'
                  }`}>
                    <div className={`mt-0.5 w-2 h-2 rounded-full flex-shrink-0 ${
                      rec.includes('Увага') || rec.includes('критичн') || rec.includes('Висока')
                        ? 'bg-red-500'
                        : rec.includes('нормальному')
                          ? 'bg-green-500'
                          : 'bg-yellow-500'
                    }`} />
                    <span className="text-sm">{rec}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Critical Issues */}
          {aiAnalysisData?.critical_issues && aiAnalysisData.critical_issues.length > 0 && (
            <div className="bg-red-50 border border-red-200 p-6 rounded-lg">
              <h2 className="text-lg font-semibold mb-4 text-red-800 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" />
                Критичні проблеми
              </h2>
              <ul className="space-y-2">
                {aiAnalysisData.critical_issues.map((issue: string, i: number) => (
                  <li key={i} className="text-sm text-red-700 flex items-start gap-2">
                    <span className="text-red-500 mt-1">•</span>
                    {issue}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Predicted Issues */}
          {aiAnalysisData?.predicted_issues && aiAnalysisData.predicted_issues.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 p-6 rounded-lg">
              <h2 className="text-lg font-semibold mb-4 text-yellow-800">Прогнозовані проблеми</h2>
              <ul className="space-y-2">
                {aiAnalysisData.predicted_issues.map((issue: string, i: number) => (
                  <li key={i} className="text-sm text-yellow-700 flex items-start gap-2">
                    <span className="text-yellow-500 mt-1">⚠</span>
                    {issue}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Suggested Actions */}
          {aiAnalysisData?.suggested_actions && aiAnalysisData.suggested_actions.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 p-6 rounded-lg">
              <h2 className="text-lg font-semibold mb-4 text-blue-800">Рекомендовані дії</h2>
              <ol className="space-y-2">
                {aiAnalysisData.suggested_actions.map((action: string, i: number) => (
                  <li key={i} className="text-sm text-blue-700 flex items-start gap-2">
                    <span className="bg-blue-200 text-blue-800 rounded-full w-5 h-5 flex items-center justify-center text-xs flex-shrink-0 mt-0.5">{i + 1}</span>
                    {action}
                  </li>
                ))}
              </ol>
            </div>
          )}

          {/* Problem Batteries */}
          {aiAnalysisData?.problem_batteries && aiAnalysisData.problem_batteries.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h2 className="text-lg font-semibold mb-4">Батареї що потребують уваги</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Батарея</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Обладнання</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Заряд</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Темп</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Інциденти</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Статус</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {aiAnalysisData.problem_batteries.map((item: any, i: number) => (
                      <tr key={i} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm text-gray-900">{item.serial_number}</td>
                        <td className="px-4 py-3 text-sm text-gray-500">{item.equipment_name}</td>
                        <td className="px-4 py-3 text-sm">
                          <span className={`${item.avg_charge < 20 ? 'text-red-600 font-semibold' : 'text-gray-900'}`}>
                            {item.avg_charge}%
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <span className={`${item.avg_temp > 60 ? 'text-red-600 font-semibold' : 'text-gray-900'}`}>
                            {item.avg_temp}°C
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">{item.incident_count}</td>
                        <td className="px-4 py-3 text-sm">
                          <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                            item.status === 'Перегрів' ? 'bg-red-100 text-red-800' :
                            item.status === 'Низький заряд' ? 'bg-orange-100 text-orange-800' :
                            item.status === 'Часті інциденти' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {item.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Trends Chart */}
          {aiAnalysisData?.trends && aiAnalysisData.trends.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h2 className="text-lg font-semibold mb-4">Тренди за останні 7 днів</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={aiAnalysisData.trends}>
                    <defs>
                      <linearGradient id="colorCharge" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" tickFormatter={(val) => val ? new Date(val).toLocaleDateString('uk-UA', { weekday: 'short', day: 'numeric' }) : ''} />
                    <YAxis yAxisId="left" domain={[0, 100]} />
                    <YAxis yAxisId="right" orientation="right" domain={[0, 80]} />
                    <Tooltip />
                    <Area yAxisId="left" type="monotone" dataKey="avg_charge" stroke="#3b82f6" fillOpacity={1} fill="url(#colorCharge)" name="Заряд %" />
                    <Area yAxisId="right" type="monotone" dataKey="avg_temp" stroke="#f59e0b" fillOpacity={1} fill="url(#colorTemp)" name="Темп °C" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ReportsPage
