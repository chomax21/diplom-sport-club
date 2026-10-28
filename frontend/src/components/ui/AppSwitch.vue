<script setup lang="ts">
import { Switch, SwitchDescription, SwitchGroup, SwitchLabel } from '@headlessui/vue'
import { computed, useId } from 'vue'

const model = defineModel<boolean>({ default: false })

const props = withDefaults(
  defineProps<{
    id?: string
    label: string
    description?: string
    error?: string | null
    disabled?: boolean
  }>(),
  {
    disabled: false,
  },
)

const generatedId = useId()
const switchId = computed(() => props.id ?? `switch-${generatedId}`)
const errorId = computed(() => `${switchId.value}-error`)
</script>

<template>
  <SwitchGroup as="div" class="min-w-0">
    <div class="flex min-h-11 items-center justify-between gap-4">
      <span class="min-w-0">
        <SwitchLabel :passive="!label" class="block text-sm font-medium text-slate-700">
          {{ label }}
        </SwitchLabel>
        <SwitchDescription v-if="description" class="mt-0.5 block text-xs leading-5 text-slate-400">
          {{ description }}
        </SwitchDescription>
      </span>

      <Switch
        :id="switchId"
        v-model="model"
        :disabled="disabled"
        class="relative inline-flex h-11 w-14 shrink-0 items-center justify-center rounded-full transition focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500 disabled:cursor-not-allowed disabled:opacity-60"
        :aria-describedby="error ? errorId : undefined"
      >
        <span
          :class="[
            'relative block h-6 w-11 rounded-full transition',
            model ? 'bg-brand-600' : 'bg-slate-300',
          ]"
        >
          <span
            :class="[
              'absolute left-0.5 top-0.5 size-5 rounded-full bg-white shadow-sm transition-transform',
              model ? 'translate-x-5' : 'translate-x-0',
            ]"
          />
        </span>
      </Switch>
    </div>
    <p v-if="error" :id="errorId" class="mt-1 text-right text-xs text-rose-600">{{ error }}</p>
  </SwitchGroup>
</template>
