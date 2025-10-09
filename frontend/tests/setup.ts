import { vi } from 'vitest'

// Mock environment variables
vi.mock('import.meta', () => ({
  env: {
    VITE_API_BASE_URL: 'http://localhost:8000/api/v1'
  }
}))

// Mock window.location
Object.defineProperty(window, 'location', {
  value: {
    hostname: 'localhost',
    reload: vi.fn(),
  },
  writable: true,
})

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  warn: vi.fn(),
  error: vi.fn(),
}