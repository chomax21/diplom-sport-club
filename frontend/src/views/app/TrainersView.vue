<script setup lang="ts">
import { Dumbbell, Plus, RefreshCw } from '@lucide/vue'
import { computed, ref, watch } from 'vue'

import type { TrainerRecord } from '@/api/directory'
import { getApiErrorMessage } from '@/api/errors'
import {
  AppBadge,
  AppButton,
  AppPagination,
  EmptyState,
  ErrorState,
  FilterBar,
  SearchInput,
  SkeletonBlock,
} from '@/components/ui'
import TrainerCard from '@/features/directory/components/TrainerCard.vue'
import TrainerFormModal from '@/features/directory/components/TrainerFormModal.vue'
import UserFormModal from '@/features/directory/components/UserFormModal.vue'
import { useTrainerListQuery } from '@/features/directory/queries'

const PAGE_SIZE = 12

const search = ref('')
const page = ref(1)

const createOpen = ref(false)
const editOpen = ref(false)
const selectedTrainer = ref<TrainerRecord | null>(null)

const params = computed(() => ({
  search: search.value.trim() || undefined,
  limit: PAGE_SIZE,
  offset: (page.value - 1) * PAGE_SIZE,
}))

const trainersQuery = useTrainerListQuery(params)

const trainers = computed<TrainerRecord[]>(() => trainersQuery.data.value?.items ?? [])
const total = computed(() => trainersQuery.data.value?.total ?? 0)

watch(search, () => {
  page.value = 1
})

function openEdit(trainer: TrainerRecord): void {
  selectedTrainer.value = trainer
  editOpen.value = true
}

function resetFilters(): void {
  search.value = ''
  page.value = 1
}
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div class="min-w-0">
        <p class="text-sm font-semibold uppercase tracking-[0.18em] text-brand-700">Клуб</p>
        <h2 class="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">Тренеры</h2>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
          Профили тренеров, специализация и контактные данные. Новый тренер создаётся как
          пользователь с ролью «Тренер».
        </p>
      </div>

      <div class="flex flex-wrap gap-2">
        <AppButton
          variant="outline"
          :loading="trainersQuery.isFetching.value"
          @click="trainersQuery.refetch()"
        >
          <template #icon>
            <RefreshCw :size="15" aria-hidden="true" />
          </template>
          Обновить
        </AppButton>
        <AppButton @click="createOpen = true">
          <template #icon>
            <Plus :size="16" aria-hidden="true" />
          </template>
          Новый тренер
        </AppButton>
      </div>
    </section>

    <div
      class="rounded-2xl border border-brand-100 bg-brand-50/70 p-4 text-xs leading-5 text-brand-800"
    >
      При создании пользователя с ролью «Тренер» профиль тренера создаётся автоматически. После
      этого специализацию и описание можно изменить в карточке.
    </div>

    <FilterBar
      :active-count="search.trim() ? 1 : 0"
      :has-active-filters="Boolean(search.trim())"
      :columns="1"
      @reset="resetFilters"
    >
      <SearchInput
        v-model="search"
        aria-label="Поиск тренеров"
        placeholder="Имя, email или специализация…"
      />
    </FilterBar>

    <div class="flex flex-wrap items-center justify-between gap-2">
      <p class="text-sm text-slate-500">
        Найдено: <span class="font-semibold text-slate-900">{{ total }}</span>
      </p>
      <AppBadge tone="info">Всего: {{ total }}</AppBadge>
    </div>

    <div v-if="trainersQuery.isPending.value" class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      <div
        v-for="index in 6"
        :key="index"
        class="rounded-card border border-slate-200 bg-white p-5 shadow-sm"
      >
        <SkeletonBlock :lines="4" avatar />
      </div>
    </div>

    <ErrorState
      v-else-if="trainersQuery.isError.value"
      title="Не удалось загрузить тренеров"
      :description="getApiErrorMessage(trainersQuery.error.value)"
      @retry="trainersQuery.refetch()"
    />

    <EmptyState
      v-else-if="trainers.length === 0"
      title="Тренеры не найдены"
      description="Создайте первого тренера или измените поисковый запрос."
      :icon="Dumbbell"
    >
      <template #actions>
        <AppButton v-if="search.trim()" variant="outline" size="sm" @click="resetFilters">
          Сбросить поиск
        </AppButton>
        <AppButton size="sm" @click="createOpen = true">
          <template #icon>
            <Plus :size="15" aria-hidden="true" />
          </template>
          Новый тренер
        </AppButton>
      </template>
    </EmptyState>

    <template v-else>
      <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <TrainerCard
          v-for="trainer in trainers"
          :key="trainer.id"
          :trainer="trainer"
          @edit="openEdit(trainer)"
        />
      </div>

      <AppPagination
        v-if="total > PAGE_SIZE"
        v-model:page="page"
        :page-size="PAGE_SIZE"
        :total="total"
      />
    </template>

    <UserFormModal
      v-model="createOpen"
      default-role="trainer"
      lock-role
      @saved="trainersQuery.refetch()"
    />

    <TrainerFormModal
      v-model="editOpen"
      :trainer="selectedTrainer"
      @saved="trainersQuery.refetch()"
    />
  </div>
</template>
