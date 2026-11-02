import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { expect, test } from 'vitest'
import { renderApp } from './render'
import { API, VALID, server } from './server'

const country = (code: string, name: string, headcount: number, avg: string) => ({
  country_code: code,
  country_name: name,
  headcount,
  min_usd: '1000.00',
  max_usd: '999999.00',
  avg_usd: avg,
})

const medians: Record<string, string> = { US: '162410.00', IN: '29003.00' }

test('shows the largest country by default and follows the country filter', async () => {
  localStorage.setItem('access_token', VALID.token)
  const titlesRequestedFor: string[] = []
  server.use(
    http.get(`${API}/insights/by-country`, () =>
      HttpResponse.json([
        country('IN', 'India', 1925, '200000.00'), // higher average, fewer people
        country('US', 'United States', 3388, '160000.00'),
      ]),
    ),
    http.get(`${API}/insights/job-titles`, () => HttpResponse.json(['Engineer'])),
    http.get(`${API}/insights/distribution`, ({ request }) => {
      const code = new URL(request.url).searchParams.get('country')!
      return HttpResponse.json({
        country_code: code,
        headcount: 1,
        p25_usd: null,
        p50_usd: medians[code],
        p75_usd: null,
        p90_usd: null,
      })
    }),
    http.get(`${API}/insights/by-title`, ({ request }) => {
      titlesRequestedFor.push(new URL(request.url).searchParams.get('country')!)
      return HttpResponse.json([])
    }),
    http.get(`${API}/insights/title-comparison`, () => HttpResponse.json([])),
  )
  const user = userEvent.setup()
  renderApp('/insights')

  // The United States has the most employees, so it is the default.
  const tiles = await screen.findByRole('heading', { name: 'Pay distribution in United States' })
  const section = tiles.closest('div.MuiPaper-root') as HTMLElement
  expect(await within(section).findByText('$162,410')).toBeInTheDocument()

  await user.click(screen.getByRole('combobox', { name: 'Country' }))
  await user.click(await screen.findByRole('option', { name: 'India' }))

  expect(await screen.findByRole('heading', { name: 'Pay distribution in India' })).toBeInTheDocument()
  expect(await screen.findByText('$29,003')).toBeInTheDocument()
  expect(titlesRequestedFor).toEqual(['US', 'IN'])
})
