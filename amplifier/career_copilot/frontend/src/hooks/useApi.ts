import { useState, useCallback } from 'react'
import toast from 'react-hot-toast'

interface UseApiOptions {
  onSuccess?: (data: any) => void
  onError?: (error: Error) => void
  showToast?: boolean
}

export function useApi<T = any>(options: UseApiOptions = {}) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const execute = useCallback(
    async (apiCall: () => Promise<T>): Promise<T | null> => {
      setLoading(true)
      setError(null)

      try {
        const result = await apiCall()

        if (options.onSuccess) {
          options.onSuccess(result)
        }

        if (options.showToast !== false) {
          // Default success toast can be handled by individual API calls
        }

        return result
      } catch (err) {
        const error = err instanceof Error ? err : new Error('An error occurred')
        setError(error)

        if (options.onError) {
          options.onError(error)
        }

        if (options.showToast !== false) {
          toast.error(error.message || 'An error occurred')
        }

        return null
      } finally {
        setLoading(false)
      }
    },
    [options.onSuccess, options.onError, options.showToast]
  )

  return {
    execute,
    loading,
    error,
    reset: () => {
      setError(null)
      setLoading(false)
    }
  }
}

// API utility functions
export const api = {
  get: async <T>(url: string): Promise<T> => {
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  },

  post: async <T>(url: string, data?: any): Promise<T> => {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined,
    })
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`)
    }
    return response.json()
  },

  put: async <T>(url: string, data?: any): Promise<T> => {
    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined,
    })
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`)
    }
    return response.json()
  },

  delete: async <T>(url: string): Promise<T> => {
    const response = await fetch(url, {
      method: 'DELETE',
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  },

  upload: async <T>(url: string, file: File): Promise<T> => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    })
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`)
    }
    return response.json()
  },
}