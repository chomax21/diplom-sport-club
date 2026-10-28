<script setup lang="ts">
import { format, subDays } from 'date-fns'
import {
  Bell,
  CalendarDays,
  Check,
  ChevronRight,
  CircleUserRound,
  Copy,
  Mail,
  Pencil,
  Plus,
  Settings2,
  Trash2,
  UserPlus,
} from '@lucide/vue'
import { computed, ref } from 'vue'

import {
  AppAvatar,
  AppBadge,
  AppButton,
  AppCheckbox,
  AppDrawer,
  AppInput,
  AppModal,
  AppPagination,
  AppSelect,
  AppSwitch,
  AppTextarea,
  AppTooltip,
  ConfirmDialog,
  DataTable,
  DatePicker,
  DateRangePicker,
  EmptyState,
  ErrorState,
  FilterBar,
  IconButton,
  LoadingState,
  SearchInput,
  SkeletonBlock,
  StatusBadge,
} from '@/components/ui'
import type { SelectOption, TableColumn, TableRow } from '@/components/ui'
import { useToastStore } from '@/stores/toasts'

const toast = useToastStore()

const iso = (date: Date): string => format(date, 'yyyy-MM-dd')
const now = new Date()

const name = ref('Иван Петров')
const email = ref('ivan@example.com')
const phone = ref('+7 999 123-45-67')
const comment = ref('')
const selectValue = ref<string | number>('trainer')
const checkboxValue = ref(true)
const switchValue = ref(true)
const dateValue = ref<string | null>(iso(now))
const rangeFrom = ref<string | null>(iso(subDays(now, 6)))
const rangeTo = ref<string | null>(iso(now))

const filterSearch = ref('')
const filterStatus = ref<string | number>('')
const filterDate = ref<string | null>(null)
const filterTrainer = ref<string | number>('')

const activeFilterCount = computed(
  () =>
    [filterSearch.value, filterStatus.value, filterDate.value, filterTrainer.value].filter(Boolean)
      .length,
)
const hasActiveFilters = computed(() => activeFilterCount.value > 0)

function resetFilters(): void {
  filterSearch.value = ''
  filterStatus.value = ''
  filterDate.value = null
  filterTrainer.value = ''
}

const selectOptions: SelectOption[] = [
  { label: 'Администратор', value: 'admin' },
  { label: 'Тренер', value: 'trainer' },
  { label: 'Клиент', value: 'client' },
]

const statusOptions: SelectOption[] = [
  { label: 'Активен', value: 'active' },
  { label: 'Ожидает', value: 'pending' },
  { label: 'Истёк', value: 'expired' },
  { label: 'Отменён', value: 'cancelled' },
]

const trainerOptions: SelectOption[] = [
  { label: 'Иван Тренеров', value: 'ivan' },
  { label: 'Мария Спортивная', value: 'maria' },
  { label: 'Пётр Сильный', value: 'petr' },
]

const modalOpen = ref(false)
const drawerOpen = ref(false)
const confirmOpen = ref(false)
const confirmLoading = ref(false)

const tableLoading = ref(false)
const tablePage = ref(2)

const columns: TableColumn[] = [
  { key: 'name', label: 'Клиент', hideOnMobile: true },
  { key: 'email', label: 'Email' },
  { key: 'membership', label: 'Абонемент' },
  { key: 'created', label: 'Добавлен' },
  { key: 'actions', label: '', align: 'right', hideOnMobile: true },
]

const rows: TableRow[] = [
  {
    id: 1,
    name: 'Анна Клиентова',
    email: 'anna@example.com',
    membership: 'active',
    created: '12.10.2026',
  },
  {
    id: 2,
    name: 'Иван Петров',
    email: 'ivan@example.com',
    membership: 'pending',
    created: '14.10.2026',
  },
  {
    id: 3,
    name: 'Мария Сидорова',
    email: 'maria@example.com',
    membership: 'expired',
    created: '01.09.2026',
  },
  {
    id: 4,
    name: 'Пётр Иванов',
    email: 'petr@example.com',
    membership: 'cancelled',
    created: '03.09.2026',
  },
]

function openConfirm(): void {
  confirmOpen.value = true
}

function confirmAction(): void {
  confirmLoading.value = true
  window.setTimeout(() => {
    confirmLoading.value = false
    confirmOpen.value = false
    toast.success('Демо-запись удалена бы, но это только UI-кит.', 'Действие подтверждено')
  }, 700)
}

function saveModal(): void {
  modalOpen.value = false
  toast.success('Демонстрационная форма сохранена.', 'Готово')
}
</script>

<template>
  <section class="space-y-6">
    <header
      class="flex flex-col gap-4 rounded-card border border-slate-200 bg-white p-5 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:p-6"
    >
      <div class="min-w-0">
        <div class="flex flex-wrap items-center gap-2">
          <AppBadge tone="brand">F3</AppBadge>
          <AppBadge tone="neutral" dot>UI-кит</AppBadge>
        </div>
        <h2 class="mt-2 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          Компоненты интерфейса
        </h2>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
          Базовые и составные компоненты, на которых строятся экраны клуба. Все элементы адаптивны,
          доступны с клавиатуры и имеют видимый focus ring.
        </p>
      </div>
      <AppButton variant="outline" @click="toast.info('Toast-уведомления работают.', 'Проверка')">
        <template #icon>
          <Bell :size="16" aria-hidden="true" />
        </template>
        Проверить toast
      </AppButton>
    </header>

    <section class="rounded-card border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <h3 class="text-lg font-semibold text-slate-900">Кнопки</h3>
      <p class="mt-1 text-sm text-slate-500">Варианты, размеры и состояния загрузки.</p>

      <div class="mt-4 flex flex-wrap items-center gap-2">
        <AppButton>Основная</AppButton>
        <AppButton variant="secondary">Тёмная</AppButton>
        <AppButton variant="outline">Контурная</AppButton>
        <AppButton variant="soft">Мягкая</AppButton>
        <AppButton variant="ghost">Прозрачная</AppButton>
        <AppButton variant="danger">Опасная</AppButton>
        <AppButton loading>Загрузка</AppButton>
        <AppButton disabled>Недоступна</AppButton>
      </div>

      <div class="mt-4 flex flex-wrap items-center gap-2">
        <AppButton size="sm">Small</AppButton>
        <AppButton size="md">Medium</AppButton>
        <AppButton size="lg">Large</AppButton>
        <AppButton>
          <template #icon>
            <Plus :size="16" aria-hidden="true" />
          </template>
          С иконкой
        </AppButton>
      </div>

      <div class="mt-4 flex flex-wrap items-center gap-2">
        <AppTooltip text="Скопировать ссылку">
          <IconButton label="Скопировать" variant="outline">
            <Copy :size="17" aria-hidden="true" />
          </IconButton>
        </AppTooltip>
        <AppTooltip text="Редактировать запись">
          <IconButton label="Редактировать" variant="soft">
            <Pencil :size="17" aria-hidden="true" />
          </IconButton>
        </AppTooltip>
        <AppTooltip text="Удалить запись">
          <IconButton label="Удалить" variant="danger">
            <Trash2 :size="17" aria-hidden="true" />
          </IconButton>
        </AppTooltip>
        <IconButton label="Настройки" variant="ghost">
          <Settings2 :size="17" aria-hidden="true" />
        </IconButton>
      </div>
    </section>

    <section class="rounded-card border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <h3 class="text-lg font-semibold text-slate-900">Формы</h3>
      <p class="mt-1 text-sm text-slate-500">
        Подписи, подсказки, ошибки и состояния disabled связаны с полями через aria-атрибуты.
      </p>

      <div class="mt-5 grid gap-4 sm:grid-cols-2">
        <AppInput
          v-model="name"
          label="Имя и фамилия"
          placeholder="Введите имя"
          hint="Так имя будет отображаться в документах"
          required
        >
          <template #prefix>
            <CircleUserRound :size="17" aria-hidden="true" />
          </template>
        </AppInput>

        <AppInput
          v-model="email"
          label="Email"
          type="email"
          placeholder="you@example.com"
          hint="Используется для входа"
        >
          <template #prefix>
            <Mail :size="17" aria-hidden="true" />
          </template>
        </AppInput>

        <AppInput
          v-model="phone"
          label="Телефон"
          type="tel"
          error="Введите номер в формате +7 999 123-45-67"
        />

        <AppInput
          v-model="name"
          label="Заблокированное поле"
          disabled
          hint="Поле недоступно для редактирования"
        />

        <AppSelect
          v-model="selectValue"
          label="Роль пользователя"
          :options="selectOptions"
          placeholder="Выберите роль"
          hint="Роль определяет доступные разделы"
        />

        <DatePicker v-model="dateValue" label="Дата тренировки" hint="Нативный ввод на мобильных" />

        <div class="sm:col-span-2">
          <AppTextarea
            v-model="comment"
            label="Комментарий"
            placeholder="Дополнительная информация…"
            hint="Не более 500 символов"
          />
        </div>

        <AppCheckbox
          v-model="checkboxValue"
          label="Согласен с правилами клуба"
          hint="Обязательно для регистрации"
        />

        <AppSwitch
          v-model="switchValue"
          label="Уведомления"
          description="Напоминания о тренировках и платежах"
        />
      </div>

      <div class="mt-5 rounded-2xl bg-slate-50 p-4">
        <p class="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">Диапазон дат</p>
        <div class="mt-3">
          <DateRangePicker
            v-model:from="rangeFrom"
            v-model:to="rangeTo"
            hint="Быстрые пресеты работают на мобильных и десктопе"
          />
        </div>
      </div>
    </section>

    <section class="rounded-card border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <h3 class="text-lg font-semibold text-slate-900">Статусы, аватары и бейджи</h3>
      <p class="mt-1 text-sm text-slate-500">
        Статусы передаются текстом и цветом одновременно, поэтому не зависят только от цвета.
      </p>

      <div class="mt-4 flex flex-wrap items-center gap-2">
        <AppBadge tone="neutral">Нейтральный</AppBadge>
        <AppBadge tone="brand" dot>Бренд</AppBadge>
        <AppBadge tone="success" dot>Успех</AppBadge>
        <AppBadge tone="warning" dot>Внимание</AppBadge>
        <AppBadge tone="danger" dot>Ошибка</AppBadge>
        <AppBadge tone="info" dot>Информация</AppBadge>
        <AppBadge tone="violet" dot>Особый</AppBadge>
      </div>

      <div class="mt-4 flex flex-wrap items-center gap-2">
        <StatusBadge kind="membership" status="active" />
        <StatusBadge kind="membership" status="pending" />
        <StatusBadge kind="membership" status="expired" />
        <StatusBadge kind="enrollment" status="attended" />
        <StatusBadge kind="enrollment" status="no_show" />
        <StatusBadge kind="payment" status="succeeded" />
        <StatusBadge kind="payment" status="refunded" />
        <StatusBadge kind="role" status="admin" />
        <StatusBadge kind="role" status="trainer" />
        <StatusBadge kind="role" status="client" />
      </div>

      <div class="mt-5 flex flex-wrap items-center gap-4">
        <AppAvatar name="Анна Клиентова" size="sm" />
        <AppAvatar name="Иван Петров" />
        <AppAvatar name="Мария Спортсменова" size="lg" />
        <div class="flex items-center gap-2 text-sm text-slate-600">
          <AppAvatar name="Пётр Сильный" size="sm" />
          <span>Тренер · Пётр Сильный</span>
        </div>
      </div>
    </section>

    <section class="rounded-card border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <h3 class="text-lg font-semibold text-slate-900">Окна и подтверждения</h3>
      <p class="mt-1 text-sm text-slate-500">
        На мобильных модальное окно и drawer занимают весь экран и закрываются по Escape.
      </p>

      <div class="mt-4 flex flex-wrap gap-2">
        <AppButton @click="modalOpen = true">
          <template #icon>
            <CalendarDays :size="16" aria-hidden="true" />
          </template>
          Открыть модальное окно
        </AppButton>
        <AppButton variant="outline" @click="drawerOpen = true">
          <template #icon>
            <Settings2 :size="16" aria-hidden="true" />
          </template>
          Открыть drawer
        </AppButton>
        <AppButton variant="danger" @click="openConfirm">
          <template #icon>
            <Trash2 :size="16" aria-hidden="true" />
          </template>
          Удалить запись
        </AppButton>
      </div>
    </section>

    <section class="rounded-card border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <h3 class="text-lg font-semibold text-slate-900">Фильтры и поиск</h3>
      <p class="mt-1 text-sm text-slate-500">
        На мобильных панель свёрнута в компактную кнопку и не занимает весь экран.
      </p>

      <div class="mt-4">
        <FilterBar
          :active-count="activeFilterCount"
          :has-active-filters="hasActiveFilters"
          @reset="resetFilters"
        >
          <SearchInput v-model="filterSearch" aria-label="Поиск клиентов" />
          <AppSelect
            v-model="filterStatus"
            label="Статус"
            :options="statusOptions"
            placeholder="Все статусы"
          />
          <AppSelect
            v-model="filterTrainer"
            label="Тренер"
            :options="trainerOptions"
            placeholder="Все тренеры"
          />
          <DatePicker v-model="filterDate" label="Дата" />
        </FilterBar>
      </div>
    </section>

    <section class="rounded-card border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 class="text-lg font-semibold text-slate-900">Таблица и пагинация</h3>
          <p class="mt-1 text-sm text-slate-500">
            На ширине меньше 768 px таблица превращается в карточки.
          </p>
        </div>
        <div class="flex items-center gap-4">
          <AppSwitch v-model="tableLoading" label="Skeleton" />
          <AppButton size="sm" variant="outline" @click="tableLoading = !tableLoading">
            Переключить
          </AppButton>
        </div>
      </div>

      <div class="mt-5">
        <DataTable
          :columns="columns"
          :rows="rows"
          :loading="tableLoading"
          mobile-title-key="name"
          row-key="id"
          empty-title="Клиентов пока нет"
          empty-text="Измените фильтры или добавьте первого клиента."
        >
          <template #cell-name="{ row }">
            <div class="flex items-center gap-2.5">
              <AppAvatar :name="String(row.name)" size="sm" />
              <span class="font-medium text-slate-900">{{ row.name }}</span>
            </div>
          </template>
          <template #cell-email="{ row }">
            <span class="text-slate-600">{{ row.email }}</span>
          </template>
          <template #cell-membership="{ row }">
            <StatusBadge kind="membership" :status="String(row.membership)" />
          </template>
          <template #cell-actions>
            <div class="flex justify-end gap-1">
              <AppTooltip text="Редактировать">
                <IconButton label="Редактировать" size="sm" variant="ghost">
                  <Pencil :size="15" aria-hidden="true" />
                </IconButton>
              </AppTooltip>
              <AppTooltip text="Удалить">
                <IconButton label="Удалить" size="sm" variant="danger">
                  <Trash2 :size="15" aria-hidden="true" />
                </IconButton>
              </AppTooltip>
            </div>
          </template>
          <template #mobile-actions>
            <IconButton label="Открыть карточку" size="sm" variant="outline">
              <ChevronRight :size="16" aria-hidden="true" />
            </IconButton>
          </template>
          <template #empty-action>
            <AppButton size="sm">
              <template #icon>
                <UserPlus :size="15" aria-hidden="true" />
              </template>
              Добавить клиента
            </AppButton>
          </template>
        </DataTable>
      </div>

      <div class="mt-5">
        <AppPagination v-model:page="tablePage" :page-size="5" :total="42" />
      </div>
    </section>

    <section class="rounded-card border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <h3 class="text-lg font-semibold text-slate-900">Состояния</h3>
      <p class="mt-1 text-sm text-slate-500">
        Loading, empty, error и skeleton используют общую типографику и отступы.
      </p>

      <div class="mt-4 grid gap-4 lg:grid-cols-2">
        <LoadingState label="Загружаем расписание" description="Это займёт пару секунд" compact />
        <EmptyState
          title="Тренировок пока нет"
          description="Создайте первую тренировку или измените период."
          compact
        >
          <template #actions>
            <AppButton size="sm">
              <template #icon>
                <Plus :size="15" aria-hidden="true" />
              </template>
              Создать
            </AppButton>
          </template>
        </EmptyState>
        <ErrorState
          title="Не удалось получить данные"
          description="Сервер вернул ошибку. Повторите запрос."
          compact
          @retry="toast.info('Повторный запрос в демо-режиме.', 'Повтор')"
        />
        <div class="rounded-2xl border border-slate-200 bg-white p-4">
          <SkeletonBlock :lines="3" avatar />
        </div>
      </div>

      <div class="mt-4 flex flex-wrap items-center gap-2 text-sm text-slate-600">
        <Check :size="16" class="text-emerald-600" aria-hidden="true" />
        Все состояния имеют семантические роли и не теряют доступность.
      </div>
    </section>
  </section>

  <AppModal
    v-model="modalOpen"
    title="Новая тренировка"
    description="Демонстрация модального окна с формой и футером."
  >
    <div class="space-y-4">
      <AppInput v-model="name" label="Название" placeholder="Групповая тренировка" />
      <div class="grid gap-4 sm:grid-cols-2">
        <DatePicker v-model="dateValue" label="Дата" />
        <AppSelect
          v-model="selectValue"
          label="Тренер"
          :options="trainerOptions"
          placeholder="Выберите тренера"
        />
      </div>
      <AppTextarea v-model="comment" label="Описание" :rows="3" />
    </div>
    <template #footer>
      <div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <AppButton variant="outline" @click="modalOpen = false">Отмена</AppButton>
        <AppButton @click="saveModal">Сохранить</AppButton>
      </div>
    </template>
  </AppModal>

  <AppDrawer
    v-model="drawerOpen"
    title="Настройки панели"
    description="Пример выезжающей панели."
    side="right"
    size="md"
  >
    <div class="space-y-5">
      <AppSwitch
        v-model="switchValue"
        label="Компактный вид"
        description="Меньше отступов в таблицах"
      />
      <AppCheckbox v-model="checkboxValue" label="Показывать подсказки" />
      <AppSelect v-model="selectValue" label="Роль по умолчанию" :options="selectOptions" />
    </div>
    <template #footer>
      <div class="flex gap-2">
        <AppButton variant="outline" block @click="drawerOpen = false">Закрыть</AppButton>
        <AppButton block @click="drawerOpen = false">Применить</AppButton>
      </div>
    </template>
  </AppDrawer>

  <ConfirmDialog
    v-model="confirmOpen"
    title="Удалить запись?"
    message="Действие нельзя отменить. Запись и связанные данные будут удалены."
    confirm-label="Удалить"
    :loading="confirmLoading"
    @confirm="confirmAction"
  />
</template>
