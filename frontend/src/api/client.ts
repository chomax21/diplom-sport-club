import axios, { type AxiosInstance } from 'axios'

import { getAccessToken } from './authToken'
import { ApiError } from './errors'

const configuredUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'

export const API_BASE_URL = configuredUrl.replace(/\/+$/, '')
export const API_ROOT_URL = API_BASE_URL.replace(/\/api\/v1$/, '')

function createHttpClient(baseURL: string, timeout: number): AxiosInstance {
  const client = axios.create({
    baseURL,
    timeout,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  client.interceptors.request.use((config) => {
    const token = getAccessToken()
    if (token) {
      config.headers.set('Authorization', `Bearer ${token}`)
    }
    return config
  })

  client.interceptors.response.use(
    (response) => response,
    (error: unknown) => Promise.reject(ApiError.from(error)),
  )

  return client
}

export const apiClient = createHttpClient(API_BASE_URL, 20_000)
export const apiRootClient = createHttpClient(API_ROOT_URL, 5_000)
