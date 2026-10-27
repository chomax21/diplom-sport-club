import { render, screen } from '@testing-library/vue'
import { describe, expect, it } from 'vitest'

import HomeView from '../HomeView.vue'

describe('HomeView', () => {
  it('renders the project title, panel link, and API address', () => {
    render(HomeView, {
      global: {
        stubs: {
          RouterLink: { template: '<a><slot /></a>' },
        },
      },
    })

    expect(screen.getByRole('heading', { name: /адаптивный интерфейс/i })).toBeTruthy()
    expect(screen.getByText('Открыть панель')).toBeTruthy()
    expect(screen.getByText('http://localhost:8000/api/v1')).toBeTruthy()
  })
})
