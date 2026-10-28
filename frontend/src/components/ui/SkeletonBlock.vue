<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    lines?: number
    avatar?: boolean
    compact?: boolean
  }>(),
  {
    lines: 3,
    avatar: false,
    compact: false,
  },
)

const lineClasses = ['w-full', 'w-5/6', 'w-2/3', 'w-3/4', 'w-1/2']
const classes = computed(() => (props.compact ? 'space-y-2' : 'space-y-3'))
</script>

<template>
  <div class="animate-pulse" role="status" aria-label="Загрузка данных">
    <div class="flex gap-3">
      <div v-if="avatar" class="size-10 shrink-0 rounded-full bg-slate-200" aria-hidden="true" />
      <div :class="['min-w-0 flex-1', classes]">
        <div
          v-for="index in lines"
          :key="index"
          :class="['h-3.5 rounded bg-slate-200', lineClasses[(index - 1) % lineClasses.length]]"
          aria-hidden="true"
        />
      </div>
    </div>
    <span class="sr-only">Загрузка данных</span>
  </div>
</template>
