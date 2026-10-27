<script setup lang="ts">
import { RouterView } from 'vue-router'

import AppErrorBoundary from '@/components/feedback/AppErrorBoundary.vue'
import ToastViewport from '@/components/feedback/ToastViewport.vue'
</script>

<template>
  <AppErrorBoundary>
    <RouterView />
  </AppErrorBoundary>
  <ToastViewport />
</template>
