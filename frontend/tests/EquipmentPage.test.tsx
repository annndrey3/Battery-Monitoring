import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import EquipmentPage from '../src/pages/EquipmentPage'

// Мок для API
vi.mock('../src/services/api', () => ({
  equipmentApi: {
    getAll: vi.fn(() => Promise.resolve({ data: [] })),
    create: vi.fn((data) => Promise.resolve({ data: { id: 1, ...data, created_at: new Date().toISOString() } })),
    update: vi.fn((id, data) => Promise.resolve({ data: { id, ...data } })),
    delete: vi.fn(() => Promise.resolve({ data: {} })),
  }
}))

describe('EquipmentPage', () => {
  it('renders page title and add button', async () => {
    render(
      <BrowserRouter>
        <EquipmentPage />
      </BrowserRouter>
    )
    
    await waitFor(() => {
      expect(screen.getByText('Оборудование')).toBeInTheDocument()
      expect(screen.getByText('Добавить')).toBeInTheDocument()
    })
  })
  
  it('opens form when clicking add button', async () => {
    const user = userEvent.setup()
    
    render(
      <BrowserRouter>
        <EquipmentPage />
      </BrowserRouter>
    )
    
    await waitFor(() => {
      const addButton = screen.getByText('Добавить')
      expect(addButton).toBeInTheDocument()
    })
    
    const addButton = screen.getByText('Добавить')
    await user.click(addButton)
    
    expect(screen.getByText('Добавить оборудование')).toBeInTheDocument()
    // Check form fields are present (using getAllByText because these appear in table header too)
    expect(screen.getAllByText('Название').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Тип').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Расположение').length).toBeGreaterThan(0)
  })
  
  it('validates required fields', async () => {
    const user = userEvent.setup()
    
    render(
      <BrowserRouter>
        <EquipmentPage />
      </BrowserRouter>
    )
    
    await waitFor(() => {
      const addButton = screen.getByText('Добавить')
      expect(addButton).toBeInTheDocument()
    })
    
    await user.click(screen.getByText('Добавить'))
    await user.click(screen.getByText('Сохранить'))
    
    // HTML5 validation should prevent submission
    expect(screen.getByText('Добавить оборудование')).toBeInTheDocument()
  })
})
