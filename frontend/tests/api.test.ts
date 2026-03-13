import { describe, it, expect, vi } from 'vitest'
import axios from 'axios'

// Мок axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
    })),
  },
}))

describe('API Services', () => {
  it('creates axios instance with correct config', async () => {
    const { api } = await import('../src/services/api')
    
    expect(axios.create).toHaveBeenCalledWith({
      baseURL: 'http://localhost:8001',
      headers: {
        'Content-Type': 'application/json',
      },
    })
  })
})
