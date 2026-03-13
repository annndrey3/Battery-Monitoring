import axios from 'axios'

const API_URL = '/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Equipment API
export const equipmentApi = {
  getAll: () => api.get('/equipment/'),
  getById: (id: number) => api.get(`/equipment/${id}`),
  create: (data: any) => api.post('/equipment/', data),
  update: (id: number, data: any) => api.put(`/equipment/${id}`, data),
  delete: (id: number) => api.delete(`/equipment/${id}`),
}

// Batteries API
export const batteriesApi = {
  getAll: (params?: { equipment_id?: number; status?: string }) => 
    api.get('/batteries/', { params }),
  getById: (id: number) => api.get(`/batteries/${id}`),
  create: (data: any) => api.post('/batteries/', data),
  update: (id: number, data: any) => api.put(`/batteries/${id}`, data),
  delete: (id: number) => api.delete(`/batteries/${id}`),
}

// Measurements API
export const measurementsApi = {
  getAll: (params?: { battery_id?: number; start_date?: string; end_date?: string }) => 
    api.get('/measurements/', { params }),
  getById: (id: number) => api.get(`/measurements/${id}`),
  create: (data: any) => api.post('/measurements/', data),
  getHistory: (batteryId: number, days?: number) => 
    api.get(`/measurements/history/${batteryId}`, { params: { days } }),
  delete: (id: number) => api.delete(`/measurements/${id}`),
}

// Incidents API
export const incidentsApi = {
  getAll: (params?: { battery_id?: number; incident_type?: string; severity?: string; is_resolved?: boolean }) => 
    api.get('/incidents/', { params }),
  getById: (id: number) => api.get(`/incidents/${id}`),
  create: (data: any) => api.post('/incidents/', data),
  update: (id: number, data: any) => api.put(`/incidents/${id}`, data),
  delete: (id: number) => api.delete(`/incidents/${id}`),
}

// Reports API
export const reportsApi = {
  getChargeLevels: () => api.get('/reports/charge-levels'),
  getTemperatureAlerts: () => api.get('/reports/temperature-alerts'),
  getIncidentStats: (months?: number) => api.get('/reports/incident-stats', { params: { months } }),
  getVoltageDeviation: () => api.get('/reports/voltage-deviation'),
  getEquipmentIncidents: (days?: number) => api.get('/reports/equipment-incidents', { params: { days } }),
  getCurrentStats: () => api.get('/reports/current-stats'),
  getEquipmentMeasurements: (days?: number) => api.get('/reports/equipment-measurements', { params: { days } }),
  getBatteryDischarge: (batteryId: number, days?: number) => 
    api.get(`/reports/battery-discharge/${batteryId}`, { params: { days } }),
  getTemperatureChart: (batteryId: number, days?: number) => 
    api.get(`/reports/temperature-chart/${batteryId}`, { params: { days } }),
  getAIAnalysis: () => api.get('/reports/ai-analysis'),
}

export default api
