import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { beforeEach, expect, test } from 'vitest'
import type { Employee } from '@/api/types'
import { renderApp } from './render'
import { API, VALID, server } from './server'

const asha: Employee = {
  id: 1,
  employee_code: 'EMP-000001',
  full_name: 'Asha Rao',
  email: 'asha@example.com',
  job_title: 'Software Engineer',
  country_code: 'IN',
  salary_amount: '2000000.00',
  salary_currency: 'INR',
  salary_usd: '21062.56',
  is_active: true,
  created_at: '2026-10-30T10:00:00Z',
  updated_at: '2026-10-30T10:00:00Z',
}
const formerEmployee: Employee = { ...asha, id: 2, full_name: 'Moved On', is_active: false }

beforeEach(() => {
  localStorage.setItem('access_token', VALID.token)
  server.use(
    http.get(`${API}/countries`, () => HttpResponse.json([{ code: 'IN', name: 'India' }])),
    http.get(`${API}/currencies`, () =>
      HttpResponse.json([
        { code: 'INR', name: 'Indian Rupee', rate_to_usd: '0.01053128', rates_as_of: '2026-10-30' },
      ]),
    ),
  )
})

test('shows salaries in local currency and USD, and filters by status', async () => {
  const requestedStatuses: string[] = []
  server.use(
    http.get(`${API}/employees`, ({ request }) => {
      const status = new URL(request.url).searchParams.get('status') ?? ''
      requestedStatuses.push(status)
      const items = status === 'inactive' ? [formerEmployee] : [asha]
      return HttpResponse.json({ items, total: items.length, page: 1, page_size: 25 })
    }),
  )
  const user = userEvent.setup()
  renderApp('/employees')

  // Indian digit grouping for INR, with the USD equivalent alongside.
  expect(await screen.findByText('₹20,00,000')).toBeInTheDocument()
  expect(screen.getByText('≈ $21,063')).toBeInTheDocument()

  await user.click(screen.getByRole('button', { name: 'Inactive' }))

  expect(await screen.findByText('Moved On')).toBeInTheDocument()
  expect(screen.queryByText('Asha Rao')).not.toBeInTheDocument()
  expect(requestedStatuses).toEqual(['active', 'inactive'])
})

test('editing a salary keeps the currency locked and saves the new amount', async () => {
  let current = asha
  let patchBody: unknown
  server.use(
    http.get(`${API}/employees`, () =>
      HttpResponse.json({ items: [current], total: 1, page: 1, page_size: 25 }),
    ),
    http.patch(`${API}/employees/1`, async ({ request }) => {
      patchBody = await request.json()
      current = { ...current, salary_amount: '2200000.00', salary_usd: '23168.82' }
      return HttpResponse.json(current)
    }),
  )
  const user = userEvent.setup()
  renderApp('/employees')

  await user.click(await screen.findByRole('button', { name: 'Edit Asha Rao' }))
  const dialog = await screen.findByRole('dialog')
  expect(within(dialog).getByLabelText('Currency')).toBeDisabled()

  const salary = within(dialog).getByLabelText('Annual salary')
  await user.clear(salary)
  await user.type(salary, '2200000')
  await user.click(within(dialog).getByRole('button', { name: 'Save' }))

  expect(await screen.findByText('₹22,00,000')).toBeInTheDocument()
  await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
  expect(patchBody).toMatchObject({ salary_amount: '2200000' })
  expect(patchBody).not.toHaveProperty('salary_currency')
})
