<script setup lang="ts">
import { ref, useId } from 'vue'

withDefaults(
  defineProps<{
    text: string
    position?: 'top' | 'bottom'
    focusable?: boolean
  }>(),
  {
    position: 'top',
    focusable: false,
  },
)

const id = `tooltip-${useId()}`
const visible = ref(false)

function show(): void {
  visible.value = true
}

function hide(): void {
  visible.value = false
}
</script>

<template>
  <span
    class="relative inline-flex"
    :tabindex="focusable ? 0 : undefined"
    @mouseenter="show"
    @mouseleave="hide"
    @focusin="show"
    @focusout="hide"
  >
    <slot />
    <Transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="opacity-0 translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-1"
    >
      <span
        v-if="visible"
        :id="id"
        role="tooltip"
        :class="[
          'pointer-events-none absolute z-50 w-max max-w-[min(16rem,80vw)] rounded-lg bg-slate-900 px-2.5 py-1.5 text-center text-xs leading-4 text-white shadow-popover',
          position === 'top'
            ? 'bottom-full left-1/2 mb-2 -translate-x-1/2'
            : 'top-full left-1/2 mt-2 -translate-x-1/2',
        ]"
      >
        {{ text }}
      </span>
    </Transition>
  </span>
</template>
