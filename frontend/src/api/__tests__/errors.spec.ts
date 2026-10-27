import { describe, expect, it } from 'vitest'

import { ApiError, getApiErrorMessage } from '../errors'

function axiosError(status: number, detail: unknown) {
  return {
    isAxiosError: true,
    message: 'Request failed',
    response: {
      status,
      data: { detail },
    },
  }
}

describe('ApiError', () => {
  it('uses backend detail as message', () => {
    const error = ApiError.from(axiosError(409, 'Нет свободных мест'))

    expect(error).toBeInstanceOf(ApiError)
    expect(error.status).toBe(409)
    expect(error.message).toBe('Нет свободных мест')
  })

  it('joins validation messages', () => {
    const error = ApiError.from(
      axiosError(422, [{ msg: 'Поле обязательно' }, { msg: 'Неверный формат' }]),
    )

    expect(error.status).toBe(422)
    expect(error.message).toBe('Поле обязательно; Неверный формат')
  })

  it('maps network failures to a readable message', () => {
    const error = ApiError.from({
      isAxiosError: true,
      message: 'Network Error',
      code: 'ERR_NETWORK',
    })

    expect(error.status).toBe(0)
    expect(getApiErrorMessage(error)).toContain('Не удалось связаться с API')
  })

  it('falls back to status message without backend detail', () => {
    const error = ApiError.from(axiosError(403, undefined))

    expect(error.message).toBe('Недостаточно прав для выполнения операции.')
  })
})
