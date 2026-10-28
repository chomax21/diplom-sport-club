<script setup lang="ts">
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { X } from '@lucide/vue'

import IconButton from './IconButton.vue'

const open = defineModel<boolean>({ default: false })

const props = withDefaults(
  defineProps<{
    title: string
    description?: string
    side?: 'left' | 'right'
    size?: 'sm' | 'md' | 'lg'
    preventClose?: boolean
  }>(),
  {
    side: 'right',
    size: 'md',
    preventClose: false,
  },
)

const sizeClasses = {
  sm: 'sm:max-w-sm',
  md: 'sm:max-w-md',
  lg: 'sm:max-w-xl',
}

function handleClose(): void {
  if (!props.preventClose) {
    open.value = false
  }
}
</script>

<template>
  <TransitionRoot as="template" :show="open">
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

      <div class="fixed inset-0 flex" :class="side === 'right' ? 'justify-end' : 'justify-start'">
        <TransitionChild
          as="template"
          enter="transition ease-in-out duration-200 transform"
          :enter-from-class="side === 'right' ? 'translate-x-full' : '-translate-x-full'"
          enter-to-class="translate-x-0"
          leave="transition ease-in-out duration-200 transform"
          leave-from-class="translate-x-0"
          :leave-to-class="side === 'right' ? 'translate-x-full' : '-translate-x-full'"
        >
          <DialogPanel
            :class="[
              'flex h-dvh w-full flex-col bg-white shadow-popover',
              side === 'right' ? 'sm:border-l' : 'sm:border-r',
              'sm:border-slate-200',
              sizeClasses[size],
            ]"
          >
            <div
              class="flex shrink-0 items-start justify-between gap-4 border-b border-slate-100 px-5 py-4"
            >
              <div class="min-w-0">
                <DialogTitle class="text-lg font-semibold text-slate-900">
                  {{ title }}
                </DialogTitle>
                <p v-if="description" class="mt-1 text-sm leading-5 text-slate-500">
                  {{ description }}
                </p>
              </div>
              <IconButton label="Закрыть панель" variant="ghost" @click="open = false">
                <X :size="18" aria-hidden="true" />
              </IconButton>
            </div>

            <div class="min-h-0 flex-1 overflow-y-auto px-5 py-5">
              <slot />
            </div>

            <div v-if="$slots.footer" class="shrink-0 border-t border-slate-100 px-5 py-4">
              <slot name="footer" />
            </div>
          </DialogPanel>
        </TransitionChild>
      </div>
    </Dialog>
  </TransitionRoot>
</template>
