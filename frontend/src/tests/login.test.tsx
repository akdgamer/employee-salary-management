import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, test } from 'vitest'
import { renderApp } from './render'
import { VALID } from './server'

test('signed-out users must sign in before seeing salary pages', async () => {
  const user = userEvent.setup()
  renderApp('/employees')

  // Redirected to sign-in instead of the protected page.
  expect(await screen.findByRole('heading', { name: 'Sign in' })).toBeInTheDocument()

  await user.type(screen.getByLabelText('Username'), VALID.username)
  await user.type(screen.getByLabelText('Password'), 'wrong-password')
  await user.click(screen.getByRole('button', { name: 'Sign in' }))
  expect(await screen.findByText('Invalid username or password')).toBeInTheDocument()

  await user.clear(screen.getByLabelText('Password'))
  await user.type(screen.getByLabelText('Password'), VALID.password)
  await user.click(screen.getByRole('button', { name: 'Sign in' }))

  // Back on the page they asked for, still signed in after a reload.
  expect(await screen.findByRole('heading', { name: 'Employees' })).toBeInTheDocument()
  expect(localStorage.getItem('access_token')).toBe(VALID.token)
})
