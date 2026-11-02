import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'

/** The API at the network level, so tests exercise the real axios client. */
export const API = 'http://localhost:8000/api/v1'

export const VALID = { username: 'hr-admin', password: 'correct-horse', token: 'valid-token' }

export const server = setupServer(
  http.post(`${API}/auth/login`, async ({ request }) => {
    const { username, password } = (await request.json()) as Record<string, string>
    return username === VALID.username && password === VALID.password
      ? HttpResponse.json({ access_token: VALID.token, token_type: 'bearer' })
      : HttpResponse.json({ detail: 'Invalid username or password' }, { status: 401 })
  }),
  http.get(`${API}/auth/me`, ({ request }) =>
    request.headers.get('Authorization') === `Bearer ${VALID.token}`
      ? HttpResponse.json({ id: 1, username: VALID.username })
      : HttpResponse.json({ detail: 'Not authenticated' }, { status: 401 }),
  ),
  // Defaults so any page can render; tests override these with server.use().
  http.get(`${API}/employees`, () =>
    HttpResponse.json({ items: [], total: 0, page: 1, page_size: 25 }),
  ),
  http.get(`${API}/countries`, () => HttpResponse.json([])),
  http.get(`${API}/currencies`, () => HttpResponse.json([])),
)
