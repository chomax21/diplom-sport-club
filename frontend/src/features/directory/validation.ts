import { toValue, type MaybeRefOrGetter } from 'vue'
import { z } from 'zod'

const phoneSchema = z.string().trim().max(30, 'Не больше 30 символов')
const fullNameSchema = z
  .string({ error: 'Введите имя' })
  .trim()
  .min(2, 'Минимум 2 символа')
  .max(255, 'Не больше 255 символов')

export const clientEditSchema = z.object({
  full_name: fullNameSchema,
  phone: phoneSchema,
  birth_date: z.string().nullable(),
  emergency_contact: z.string().trim().max(255, 'Не больше 255 символов'),
  notes: z.string().max(2000, 'Не больше 2000 символов'),
})

export type ClientEditValues = z.infer<typeof clientEditSchema>

export const trainerEditSchema = z.object({
  full_name: fullNameSchema,
  phone: phoneSchema,
  specialization: z.string().trim().max(255, 'Не больше 255 символов'),
  bio: z.string().max(2000, 'Не больше 2000 символов'),
})

export type TrainerEditValues = z.infer<typeof trainerEditSchema>

export const roomFormSchema = z.object({
  name: z
    .string({ error: 'Введите название' })
    .trim()
    .min(1, 'Введите название')
    .max(120, 'Не больше 120 символов'),
  capacity: z
    .string({ error: 'Укажите вместимость' })
    .trim()
    .min(1, 'Укажите вместимость')
    .refine((value) => /^\d+$/.test(value), 'Введите целое число')
    .refine((value) => {
      const number = Number(value)
      return number >= 1 && number <= 10_000
    }, 'Вместимость — от 1 до 10 000'),
  description: z.string().max(2000, 'Не больше 2000 символов'),
  is_active: z.boolean(),
})

export type RoomFormValues = z.infer<typeof roomFormSchema>

const userBaseSchema = z.object({
  email: z.string().trim().max(255, 'Не больше 255 символов'),
  password: z.string().max(128, 'Не больше 128 символов'),
  password_confirm: z.string().max(128, 'Не больше 128 символов'),
  full_name: fullNameSchema,
  phone: phoneSchema,
  role: z.string().min(1, 'Выберите роль'),
})

export type UserFormValues = z.infer<typeof userBaseSchema>

export function createUserFormSchema(options: { editing: MaybeRefOrGetter<boolean> }) {
  return userBaseSchema.superRefine((values, context) => {
    if (!['admin', 'trainer', 'client'].includes(values.role)) {
      context.addIssue({
        code: 'custom',
        message: 'Выберите роль',
        path: ['role'],
      })
    }

    if (toValue(options.editing)) {
      return
    }

    if (!values.email) {
      context.addIssue({
        code: 'custom',
        message: 'Введите email',
        path: ['email'],
      })
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
      context.addIssue({
        code: 'custom',
        message: 'Некорректный email',
        path: ['email'],
      })
    }

    if (values.password.length < 8) {
      context.addIssue({
        code: 'custom',
        message: 'Пароль должен содержать минимум 8 символов',
        path: ['password'],
      })
    }

    if (values.password !== values.password_confirm) {
      context.addIssue({
        code: 'custom',
        message: 'Пароли не совпадают',
        path: ['password_confirm'],
      })
    }
  })
}
