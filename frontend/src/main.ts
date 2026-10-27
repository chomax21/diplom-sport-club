import './assets/main.css'

import { VueQueryPlugin } from '@tanstack/vue-query'
import { createApp } from 'vue'

import App from './App.vue'
import { getApiErrorMessage } from './api/errors'
import { pinia } from './app/pinia'
import { queryClient } from './app/queryClient'
import router from './router'
import { useToastStore } from './stores/toasts'

const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(VueQueryPlugin, { queryClient })

app.config.errorHandler = (error, _instance, info) => {
  console.error('[Vue]', error, info)
  useToastStore(pinia).error(getApiErrorMessage(error), 'Ошибка интерфейса')
}

app.mount('#app')
