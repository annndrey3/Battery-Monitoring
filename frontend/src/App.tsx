import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import EquipmentPage from './pages/EquipmentPage'
import BatteriesPage from './pages/BatteriesPage'
import MeasurementsPage from './pages/MeasurementsPage'
import IncidentsPage from './pages/IncidentsPage'
import ReportsPage from './pages/ReportsPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="equipment" element={<EquipmentPage />} />
          <Route path="batteries" element={<BatteriesPage />} />
          <Route path="measurements" element={<MeasurementsPage />} />
          <Route path="incidents" element={<IncidentsPage />} />
          <Route path="reports" element={<ReportsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
