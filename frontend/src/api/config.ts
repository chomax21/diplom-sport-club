const configuredUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'

export const API_BASE_URL = configuredUrl.replace(/\/+$/, '')
export const API_ROOT_URL = API_BASE_URL.replace(/\/api\/v1$/, '')
