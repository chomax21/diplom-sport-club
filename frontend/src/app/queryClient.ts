import { MutationCache, QueryCache, QueryClient } from '@tanstack/vue-query'

import { getApiErrorMessage } from '@/api/errors'
import { pinia } from '@/app/pinia'
import { useToastStore } from '@/stores/toasts'

export const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (error, query) => {
      if (query.meta?.silent) {
        return
      }

      useToastStore(pinia).error(getApiErrorMessage(error), 'Не удалось загрузить данные')
    },
  }),
  mutationCache: new MutationCache({
    onError: (error, _variables, _context, mutation) => {
      if (mutation.meta?.silent) {
        return
      }

      useToastStore(pinia).error(getApiErrorMessage(error), 'Не удалось выполнить действие')
    },
  }),
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
})
