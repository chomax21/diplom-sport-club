import axios from 'axios'

export interface ValidationIssue {
  loc?: Array<string | number>
  msg?: string
  type?: string
}

export type ApiErrorDetails = string | ValidationIssue[] | null

function normalizeDetails(detail: unknown): ApiErrorDetails {
  if (typeof detail === 'string') {
    return detail
  }

  if (Array.isArray(detail)) {
    return detail.filter(
      (item): item is ValidationIssue => typeof item === 'object' && item !== null,
    )
  }

  return null
}

function detailsToMessage(details: ApiErrorDetails): string | null {
  if (typeof details === 'string') {
    return details
  }

  if (Array.isArray(details)) {
    const messages = details
      .map((item) => item.msg)
      .filter((message): message is string => Boolean(message))

    return messages.length > 0 ? messages.slice(0, 3).join('; ') : null
  }

  return null
}

function statusMessage(status: number): string {
  if (status === 401) {
    return 'Требуется авторизация.'
  }
  if (status === 403) {
    return 'Недостаточно прав для выполнения операции.'
  }
  if (status === 404) {
    return 'Запрошенный объект не найден.'
  }
  if (status === 409) {
    return 'Конфликт данных. Проверьте введённые значения.'
  }
  if (status === 422) {
    return 'Проверьте правильность заполнения полей.'
  }
  if (status === 502) {
    return 'Ошибка платёжного провайдера. Попробуйте позже.'
  }
  if (status === 503) {
    return 'Сервис временно недоступен.'
  }
  if (status >= 500) {
    return 'Ошибка сервера. Попробуйте позже.'
  }
  return 'Не удалось выполнить запрос.'
}

export class ApiError extends Error {
  readonly status: number
  readonly details: ApiErrorDetails

  constructor(message: string, status = 0, details: ApiErrorDetails = null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.details = details
  }

  static from(error: unknown): ApiError {
    if (error instanceof ApiError) {
      return error
    }

    if (axios.isAxiosError(error)) {
      const status = error.response?.status ?? 0
      const payload = error.response?.data as { detail?: unknown } | undefined
      const details = normalizeDetails(payload?.detail)

      if (!error.response) {
        const message =
          error.code === 'ECONNABORTED'
            ? 'Сервер не ответил вовремя. Попробуйте ещё раз.'
            : 'Не удалось связаться с API. Проверьте, что бэкенд запущен.'

        return new ApiError(message, 0, details)
      }

      return new ApiError(detailsToMessage(details) ?? statusMessage(status), status, details)
    }

    if (error instanceof Error) {
      return new ApiError(error.message)
    }

    return new ApiError('Неизвестная ошибка')
  }
}

export function getApiErrorMessage(error: unknown): string {
  return ApiError.from(error).message
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError
}
