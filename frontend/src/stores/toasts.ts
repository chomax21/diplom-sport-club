import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface Toast {
  id: number
  type: ToastType
  title: string
  message?: string
}

interface ToastOptions {
  type?: ToastType
  title: string
  message?: string
  timeout?: number
}

const DEFAULT_TIMEOUT = 4_500
const ERROR_TIMEOUT = 7_000

export const useToastStore = defineStore('toasts', () => {
  const items = ref<Toast[]>([])
  const timers = new Map<number, ReturnType<typeof setTimeout>>()
  let nextId = 1

  function remove(id: number): void {
    const timer = timers.get(id)
    if (timer) {
      clearTimeout(timer)
      timers.delete(id)
    }

    items.value = items.value.filter((toast) => toast.id !== id)
  }

  function push(options: ToastOptions): number {
    const id = nextId
    nextId += 1

    const type = options.type ?? 'info'
    const timeout = options.timeout ?? (type === 'error' ? ERROR_TIMEOUT : DEFAULT_TIMEOUT)

    items.value.push({
      id,
      type,
      title: options.title,
      message: options.message,
    })

    if (timeout > 0) {
      timers.set(
        id,
        setTimeout(() => remove(id), timeout),
      )
    }

    return id
  }

  function success(message: string, title = 'Готово'): number {
    return push({ type: 'success', title, message })
  }

  function error(message: string, title = 'Ошибка'): number {
    return push({ type: 'error', title, message })
  }

  function warning(message: string, title = 'Внимание'): number {
    return push({ type: 'warning', title, message })
  }

  function info(message: string, title = 'Информация'): number {
    return push({ type: 'info', title, message })
  }

  function clear(): void {
    timers.forEach((timer) => clearTimeout(timer))
    timers.clear()
    items.value = []
  }

  return {
    items,
    push,
    remove,
    success,
    error,
    warning,
    info,
    clear,
  }
})
