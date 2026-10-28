export type ClassValue =
  string | number | null | undefined | false | Record<string, boolean> | ClassValue[]

/**
 * Объединяет классы, отбрасывая пустые значения. Нужен для вариантов
 * компонентов, чтобы не собирать длинные тернарные выражения в шаблонах.
 */
export function cn(...values: ClassValue[]): string {
  const classes: string[] = []

  for (const value of values) {
    if (!value) {
      continue
    }

    if (typeof value === 'string' || typeof value === 'number') {
      classes.push(String(value))
      continue
    }

    if (Array.isArray(value)) {
      const nested = cn(...value)
      if (nested) {
        classes.push(nested)
      }
      continue
    }

    for (const [className, enabled] of Object.entries(value)) {
      if (enabled) {
        classes.push(className)
      }
    }
  }

  return classes.join(' ')
}
