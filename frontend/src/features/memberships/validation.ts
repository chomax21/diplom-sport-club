import { z } from 'zod'

function numberString(options: {
  required: string
  integer: string
  min: number
  max: number
  range: string
}) {
  return z
    .string({ error: options.required })
    .trim()
    .min(1, options.required)
    .refine((value) => /^\d+$/.test(value), options.integer)
    .refine((value) => {
      const number = Number(value)
      return Number.isInteger(number) && number >= options.min && number <= options.max
    }, options.range)
}

export const membershipTypeSchema = z.object({
  name: z
    .string({ error: 'Введите название' })
    .trim()
    .min(2, 'Минимум 2 символа')
    .max(120, 'Не больше 120 символов'),
  description: z.string().max(2000, 'Описание не должно превышать 2000 символов'),
  price: z
    .string({ error: 'Укажите стоимость' })
    .trim()
    .min(1, 'Укажите стоимость')
    .refine(
      (value) => /^\d+(?:[.,]\d{1,2})?$/.test(value),
      'Введите сумму, например 4500 или 4500.50',
    )
    .refine(
      (value) => Number(value.replace(',', '.')) >= 0,
      'Стоимость не может быть отрицательной',
    )
    .refine(
      (value) => Number(value.replace(',', '.')) <= 99_999_999.99,
      'Слишком большая стоимость',
    ),
  duration_days: numberString({
    required: 'Укажите срок действия',
    integer: 'Введите целое число дней',
    min: 1,
    max: 3650,
    range: 'Срок — от 1 до 3650 дней',
  }),
  visits_limit: z
    .string()
    .trim()
    .refine(
      (value) =>
        value === '' || (/^\d+$/.test(value) && Number(value) >= 1 && Number(value) <= 10000),
      'Введите целое число от 1 до 10000 или оставьте поле пустым',
    ),
  is_active: z.boolean(),
})

export type MembershipTypeFormValues = z.infer<typeof membershipTypeSchema>
