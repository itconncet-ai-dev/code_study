import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios, { AxiosError, AxiosHeaders } from 'axios'
import {
  apiClient,
  ApiClientError,
  ApiError,
  get,
  post,
  patch,
  put,
  del,
  uploadFiles,
} from './api-client'

// Mock axios
vi.mock('axios', async () => {
  const actual = await vi.importActual('axios')
  return {
    ...actual,
    default: {
      create: vi.fn(() => ({
        get: vi.fn(),
        post: vi.fn(),
        patch: vi.fn(),
        put: vi.fn(),
        delete: vi.fn(),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() },
        },
      })),
      post: vi.fn(),
    },
  }
})

describe('ApiClientError', () => {
  it('should create error with message from response', () => {
    const axiosError = {
      message: 'Request failed',
      response: {
        status: 400,
        data: { error: 'Invalid input', detail: 'Email is required' },
      },
    } as AxiosError<ApiError>

    const error = new ApiClientError(axiosError)

    expect(error.message).toBe('Invalid input')
    expect(error.status).toBe(400)
    expect(error.data?.detail).toBe('Email is required')
  })

  it('should use axios message when no response data', () => {
    const axiosError = {
      message: 'Network Error',
      response: undefined,
    } as AxiosError<ApiError>

    const error = new ApiClientError(axiosError)

    expect(error.message).toBe('Network Error')
    expect(error.status).toBe(0)
  })

  it('should correctly identify unauthorized errors', () => {
    const error = new ApiClientError({
      message: 'Unauthorized',
      response: { status: 401, data: { error: 'Unauthorized' } },
    } as AxiosError<ApiError>)

    expect(error.isUnauthorized()).toBe(true)
    expect(error.isForbidden()).toBe(false)
  })

  it('should correctly identify forbidden errors', () => {
    const error = new ApiClientError({
      message: 'Forbidden',
      response: { status: 403, data: { error: 'Forbidden' } },
    } as AxiosError<ApiError>)

    expect(error.isForbidden()).toBe(true)
    expect(error.isUnauthorized()).toBe(false)
  })

  it('should correctly identify not found errors', () => {
    const error = new ApiClientError({
      message: 'Not Found',
      response: { status: 404, data: { error: 'Not Found' } },
    } as AxiosError<ApiError>)

    expect(error.isNotFound()).toBe(true)
  })

  it('should correctly identify validation errors', () => {
    const error = new ApiClientError({
      message: 'Bad Request',
      response: { status: 400, data: { error: 'Validation failed' } },
    } as AxiosError<ApiError>)

    expect(error.isValidationError()).toBe(true)
  })

  it('should correctly identify server errors', () => {
    const error500 = new ApiClientError({
      message: 'Server Error',
      response: { status: 500, data: { error: 'Internal Server Error' } },
    } as AxiosError<ApiError>)

    const error502 = new ApiClientError({
      message: 'Bad Gateway',
      response: { status: 502, data: { error: 'Bad Gateway' } },
    } as AxiosError<ApiError>)

    expect(error500.isServerError()).toBe(true)
    expect(error502.isServerError()).toBe(true)
  })
})

describe('apiClient configuration', () => {
  it('should be created with correct base URL', () => {
    expect(axios.create).toHaveBeenCalledWith(
      expect.objectContaining({
        baseURL: expect.stringContaining('/api/v1'),
        withCredentials: true,
      })
    )
  })

  it('should set default content type to JSON', () => {
    expect(axios.create).toHaveBeenCalledWith(
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
      })
    )
  })

  it('should set 30 second timeout', () => {
    expect(axios.create).toHaveBeenCalledWith(
      expect.objectContaining({
        timeout: 30000,
      })
    )
  })
})

describe('API helper functions', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('get', () => {
    it('should make GET request and return data', async () => {
      const mockData = { id: 1, name: 'Test' }
      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockData })

      const result = await get<typeof mockData>('/test')

      expect(apiClient.get).toHaveBeenCalledWith('/test', undefined)
      expect(result).toEqual(mockData)
    })
  })

  describe('post', () => {
    it('should make POST request with data and return response', async () => {
      const requestData = { email: 'test@example.com' }
      const responseData = { id: 1 }
      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: responseData })

      const result = await post<typeof responseData>('/test', requestData)

      expect(apiClient.post).toHaveBeenCalledWith(
        '/test',
        requestData,
        undefined
      )
      expect(result).toEqual(responseData)
    })
  })

  describe('patch', () => {
    it('should make PATCH request with data', async () => {
      const updateData = { name: 'Updated' }
      vi.mocked(apiClient.patch).mockResolvedValueOnce({ data: updateData })

      const result = await patch('/test/1', updateData)

      expect(apiClient.patch).toHaveBeenCalledWith(
        '/test/1',
        updateData,
        undefined
      )
      expect(result).toEqual(updateData)
    })
  })

  describe('put', () => {
    it('should make PUT request with data', async () => {
      const putData = { name: 'Replaced' }
      vi.mocked(apiClient.put).mockResolvedValueOnce({ data: putData })

      const result = await put('/test/1', putData)

      expect(apiClient.put).toHaveBeenCalledWith('/test/1', putData, undefined)
      expect(result).toEqual(putData)
    })
  })

  describe('del', () => {
    it('should make DELETE request', async () => {
      vi.mocked(apiClient.delete).mockResolvedValueOnce({ data: undefined })

      await del('/test/1')

      expect(apiClient.delete).toHaveBeenCalledWith('/test/1', undefined)
    })
  })

  describe('uploadFiles', () => {
    it('should make POST request with multipart/form-data content type', async () => {
      const formData = new FormData()
      formData.append('file', new Blob(['test']), 'test.txt')
      const responseData = { id: 1, filename: 'test.txt' }
      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: responseData })

      const result = await uploadFiles<typeof responseData>('/upload', formData)

      expect(apiClient.post).toHaveBeenCalledWith('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      expect(result).toEqual(responseData)
    })
  })
})

describe('Error handling', () => {
  it('should throw ApiClientError on request failure', async () => {
    const axiosError = new AxiosError('Request failed')
    axiosError.response = {
      status: 500,
      statusText: 'Internal Server Error',
      data: { error: 'Server error' },
      headers: {},
      config: { headers: new AxiosHeaders() },
    }

    vi.mocked(apiClient.get).mockRejectedValueOnce(
      new ApiClientError(axiosError as AxiosError<ApiError>)
    )

    await expect(get('/test')).rejects.toThrow(ApiClientError)
  })
})
