import { toValue, type MaybeRefOrGetter } from 'vue'
import { z } from 'zod'

import type { Room } from '@/api/schedule'

const baseSchema = z.object({
  title: z
    .string({ error: 'Введите название' })
    .trim()
    .min(2, 'Минимум 2 символа')
    .max(255, 'Слишком длинное название'),
  room_id: z.string({ error: 'Выберите зал' }).min(1, 'Выберите зал'),
  trainer_id: z.string({ error: 'Выберите тренера' }),
  date: z
    .string({ error: 'Укажите дату' })
    .min(1, 'Укажите дату')
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Некорректная дата'),
  start_time: z
    .string({ error: 'Укажите время начала' })
    .min(1, 'Укажите время начала')
    .regex(/^\d{2}:\d{2}$/, 'Некорректное время'),
  end_time: z
    .string({ error: 'Укажите время окончания' })
    .min(1, 'Укажите время окончания')
    .regex(/^\d{2}:\d{2}$/, 'Некорректное время'),
  capacity: z
    .string({ error: 'Укажите вместимость' })
    .min(1, 'Укажите вместимость')
    .refine(
      (value) => Number.isInteger(Number(value)) && Number(value) > 0,
      'Введите целое число больше нуля',
    ),
  description: z.string().max(2000, 'Описание не должно превышать 2000 символов'),
})

export type SessionFormValues = z.infer<typeof baseSchema>

interface SessionSchemaOptions {
  requireTrainer: MaybeRefOrGetter<boolean>
  rooms: MaybeRefOrGetter<Room[]>
}

export function createSessionSchema(options: SessionSchemaOptions) {
  return baseSchema.superRefine((values, context) => {
    if (toValue(options.requireTrainer) && !values.trainer_id) {
      context.addIssue({
        code: 'custom',
        message: 'Выберите тренера',
        path: ['trainer_id'],
      })
    }

    if (values.start_time && values.end_time && values.end_time <= values.start_time) {
      context.addIssue({
        code: 'custom',
        message: 'Окончание должно быть позже начала',
        path: ['end_time'],
      })
    }

    const room = toValue(options.rooms).find((item) => item.id === values.room_id)
    if (room && Number(values.capacity) > room.capacity) {
      context.addIssue({
        code: 'custom',
        message: `Вместимость зала — не больше ${room.capacity}`,
        path: ['capacity'],
      })
    }
  })
}
