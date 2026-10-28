<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { userInitials } from '@/lib/roles'

const props = withDefaults(
  defineProps<{
    name: string
    src?: string | null
    size?: 'sm' | 'md' | 'lg'
  }>(),
  {
    src: null,
    size: 'md',
  },
)

const failed = ref(false)

watch(
  () => props.src,
  () => {
    failed.value = false
  },
)

const sizeClasses = {
  sm: 'size-8 text-[11px]',
  md: 'size-10 text-sm',
  lg: 'size-14 text-lg',
}

const initials = computed(() => userInitials(props.name))
</script>

<template>
  <span
    :class="[
      'inline-grid shrink-0 place-items-center overflow-hidden rounded-full bg-brand-50 font-bold text-brand-700 ring-1 ring-brand-100',
      sizeClasses[size],
    ]"
  >
    <img
      v-if="src && !failed"
      :src="src"
      :alt="name"
      class="size-full object-cover"
      @error="failed = true"
    />
    <template v-else>
      <span aria-hidden="true">{{ initials }}</span>
      <span class="sr-only">{{ name }}</span>
    </template>
  </span>
</template>
