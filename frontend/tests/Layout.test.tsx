import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Layout from '../src/components/Layout'

// Мок для React Router
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    Outlet: () => <div data-testid="outlet">Page Content</div>,
    Link: ({ children, to }: { children: any; to: string }) => (
      <a href={to} data-testid={`link-${to}`}>{children}</a>
    ),
    useLocation: () => ({ pathname: '/' }),
  }
})

describe('Layout Component', () => {
  it('renders navigation menu', () => {
    render(
      <BrowserRouter>
        <Layout />
      </BrowserRouter>
    )
    
    // Check navigation items
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Оборудование')).toBeInTheDocument()
    expect(screen.getByText('Батареи')).toBeInTheDocument()
    expect(screen.getByText('Измерения')).toBeInTheDocument()
    expect(screen.getByText('Инциденты')).toBeInTheDocument()
    expect(screen.getByText('Отчеты')).toBeInTheDocument()
  })
  
  it('renders outlet for page content', () => {
    render(
      <BrowserRouter>
        <Layout />
      </BrowserRouter>
    )
    
    expect(screen.getByTestId('outlet')).toBeInTheDocument()
    expect(screen.getByText('Page Content')).toBeInTheDocument()
  })
})
