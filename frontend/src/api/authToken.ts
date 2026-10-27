const REFRESH_TOKEN_KEY = 'sports-club.refresh-token'

let accessToken: string | null = null

export function getAccessToken(): string | null {
  return accessToken
}

export function setAccessToken(token: string | null): void {
  accessToken = token
}

export function getRefreshToken(): string | null {
  if (typeof window === 'undefined') {
    return null
  }

  return window.localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function setRefreshToken(token: string | null): void {
  if (typeof window === 'undefined') {
    return
  }

  if (token) {
    window.localStorage.setItem(REFRESH_TOKEN_KEY, token)
  } else {
    window.localStorage.removeItem(REFRESH_TOKEN_KEY)
  }
}

export function clearTokens(): void {
  accessToken = null
  setRefreshToken(null)
}
