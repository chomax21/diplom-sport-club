import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'

import { getAccessToken } from './authToken'
import { API_BASE_URL, API_ROOT_URL } from './config'
import { ApiError } from './errors'
import { refreshAccessToken } from './session'

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _authRetried?: boolean
}

function isAuthEndpoint(url: string | undefined): boolean {
  if (!url) {
    return false
  }

  return /\/auth\/(login|token|register|refresh)(?:\?|$)/.test(url)
}

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
    async (error: unknown) => {
      if (axios.isAxiosError(error)) {
        const config = error.config as RetryableRequestConfig | undefined
        const shouldRefresh =
          error.response?.status === 401 &&
          config !== undefined &&
          config._authRetried !== true &&
          !isAuthEndpoint(config.url)

        if (shouldRefresh) {
          config._authRetried = true
          const token = await refreshAccessToken()

          if (token) {
            config.headers.set('Authorization', `Bearer ${token}`)
            return client.request(config)
          }
        }
      }

      return Promise.reject(ApiError.from(error))
    },
  )

  return client
}

export const apiClient = createHttpClient(API_BASE_URL, 20_000)
export const apiRootClient = createHttpClient(API_ROOT_URL, 5_000)
