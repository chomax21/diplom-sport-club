<script setup lang="ts">
import {
  Dialog,
  DialogDescription,
  DialogPanel,
  DialogTitle,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue'
import { X } from '@lucide/vue'
import { watch } from 'vue'

import IconButton from './IconButton.vue'

const open = defineModel<boolean>({ default: false })

let previousFocus: HTMLElement | null = null

watch(open, (isOpen) => {
  if (isOpen) {
    previousFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null
  }
})

function restoreFocus(): void {
  const target = previousFocus
  previousFocus = null

  if (!target?.isConnected) {
    return
  }

  window.setTimeout(() => target.focus({ preventScroll: true }), 0)
}

const props = withDefaults(
  defineProps<{
    title: string
    description?: string
    size?: 'sm' | 'md' | 'lg'
    preventClose?: boolean
  }>(),
  {
    size: 'md',
    preventClose: false,
  },
)

const sizeClasses = {
  sm: 'sm:max-w-md',
  md: 'sm:max-w-xl',
  lg: 'sm:max-w-3xl',
}

function handleClose(): void {
  if (!props.preventClose) {
    open.value = false
  }
}
</script>

<template>
  <TransitionRoot as="template" :show="open" @after-leave="restoreFocus">
    <Dialog as="div" class="fixed inset-0 z-50" @close="handleClose">
      <TransitionChild
        as="template"
        enter="transition-opacity ease-out duration-200"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="transition-opacity ease-in duration-150"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-slate-950/60 backdrop-blur-[2px]" aria-hidden="true" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-stretch justify-center sm:items-center sm:p-4">
          <TransitionChild
            as="template"
            enter="transition ease-out duration-200 transform"
            enter-from="opacity-0 translate-y-4 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100"
            leave="transition ease-in duration-150 transform"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:scale-95"
          >
            <DialogPanel
              :class="[
                'relative flex h-dvh w-full flex-col bg-white shadow-popover sm:h-auto sm:max-h-[90dvh] sm:rounded-card sm:border sm:border-slate-200',
                sizeClasses[size],
              ]"
            >
              <div
                class="flex shrink-0 items-start justify-between gap-4 border-b border-slate-100 px-5 py-4 sm:px-6"
              >
                <div class="min-w-0">
                  <DialogTitle class="text-lg font-semibold text-slate-900">
                    {{ title }}
                  </DialogTitle>
                  <DialogDescription
                    v-if="description"
                    class="mt-1 text-sm leading-5 text-slate-500"
                  >
                    {{ description }}
                  </DialogDescription>
                </div>
                <IconButton label="Закрыть окно" variant="ghost" @click="open = false">
                  <X :size="18" aria-hidden="true" />
                </IconButton>
              </div>

              <div class="min-h-0 flex-1 overflow-y-auto px-5 py-5 sm:px-6">
                <slot />
              </div>

              <div
                v-if="$slots.footer"
                class="shrink-0 border-t border-slate-100 bg-slate-50/70 px-5 py-4 sm:px-6"
              >
                <slot name="footer" />
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>
