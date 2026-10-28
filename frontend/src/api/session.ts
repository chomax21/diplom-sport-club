import axios from 'axios'

import { API_BASE_URL } from './config'
import { clearTokens, getRefreshToken, setAccessToken, setRefreshToken } from './authToken'
import type { TokenPair } from './types'

type SessionExpiredHandler = () => void

const sessionExpiredHandlers = new Set<SessionExpiredHandler>()

let refreshPromise: Promise<string | null> | null = null

export function applyTokenPair(pair: TokenPair): void {
  setAccessToken(pair.access_token)
  setRefreshToken(pair.refresh_token)
}

export function onSessionExpired(handler: SessionExpiredHandler): () => void {
  sessionExpiredHandlers.add(handler)

  return () => {
    sessionExpiredHandlers.delete(handler)
  }
}

function emitSessionExpired(): void {
  sessionExpiredHandlers.forEach((handler) => handler())
}

function isExpiredSessionError(error: unknown): boolean {
  if (!axios.isAxiosError(error)) {
    return false
  }

  const status = error.response?.status
  return status === 400 || status === 401 || status === 403 || status === 422
}

/**
 * Обновляет access-токен по refresh-токену.
 *
 * Одновременные вызовы получают один и тот же промис, поэтому при серии
 * ответов 401 refresh выполняется один раз. При недействительном refresh-токене
 * токены очищаются, а подписчики узнают об истечении сессии.
 */
export function refreshAccessToken(silent = false): Promise<string | null> {
  if (refreshPromise) {
    return refreshPromise
  }

  const refreshToken = getRefreshToken()
  if (!refreshToken) {
    return Promise.resolve(null)
  }

  refreshPromise = (async () => {
    try {
      const { data } = await axios.post<TokenPair>(
        `${API_BASE_URL}/auth/refresh`,
        { refresh_token: refreshToken },
        {
          timeout: 15_000,
          headers: { 'Content-Type': 'application/json' },
        },
      )

      applyTokenPair(data)
      return data.access_token
    } catch (error) {
      if (isExpiredSessionError(error)) {
        clearTokens()
        if (!silent) {
          emitSessionExpired()
        }
      }

      return null
    } finally {
      refreshPromise = null
    }
  })()

  return refreshPromise
}
