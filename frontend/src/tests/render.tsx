import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { AppRoutes } from '@/App'
import { Providers } from '@/Providers'

/** Render the whole app at a URL, as a user arriving there would see it. */
export function renderApp(url: string) {
  return render(
    <MemoryRouter initialEntries={[url]}>
      <Providers>
        <AppRoutes />
      </Providers>
    </MemoryRouter>,
  )
}
