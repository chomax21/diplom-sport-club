import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import AppPagination from '../AppPagination.vue'
import StatusBadge from '../StatusBadge.vue'

describe('AppPagination', () => {
  it('shows the current page and emits the next page', async () => {
    const wrapper = mount(AppPagination, {
      props: {
        page: 2,
        pageSize: 10,
        total: 42,
      },
    })

    expect(wrapper.get('[aria-current="page"]').text()).toBe('2')
    expect(wrapper.text()).toContain('11–20 из 42')

    await wrapper.get('button[aria-label="Следующая страница"]').trigger('click')
    expect(wrapper.emitted('update:page')?.[0]).toEqual([3])
  })

  it('does not go beyond the last page', async () => {
    const wrapper = mount(AppPagination, {
      props: {
        page: 5,
        pageSize: 10,
        total: 42,
      },
    })

    expect(
      wrapper.get('button[aria-label="Следующая страница"]').attributes('disabled'),
    ).toBeDefined()
    expect(wrapper.text()).toContain('41–42 из 42')
  })
})

describe('StatusBadge', () => {
  it('renders a human-readable status', () => {
    const wrapper = mount(StatusBadge, {
      props: {
        kind: 'payment',
        status: 'succeeded',
      },
    })

    expect(wrapper.text()).toContain('Успешно')
  })

  it('falls back to the raw status for unknown values', () => {
    const wrapper = mount(StatusBadge, {
      props: {
        kind: 'membership',
        status: 'unknown_status',
      },
    })

    expect(wrapper.text()).toContain('unknown_status')
  })
})
