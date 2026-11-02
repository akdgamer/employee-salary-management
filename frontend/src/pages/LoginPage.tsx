import { zodResolver } from '@hookform/resolvers/zod'
import { Alert, Box, Button, Paper, Stack, TextField, Typography } from '@mui/material'
import axios from 'axios'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Navigate, useLocation, useNavigate } from 'react-router'
import { z } from 'zod'
import { useAuth } from '@/auth/useAuth'

const schema = z.object({
  username: z.string().trim().min(1, 'Enter your username'),
  password: z.string().min(1, 'Enter your password'),
})
type Credentials = z.infer<typeof schema>

export function LoginPage() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [error, setError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Credentials>({ resolver: zodResolver(schema) })

  const destination = (location.state as { from?: string } | null)?.from ?? '/employees'
  if (user) return <Navigate to={destination} replace />

  const onSubmit = async ({ username, password }: Credentials) => {
    setError(null)
    try {
      await login(username, password)
      navigate(destination, { replace: true })
    } catch (e) {
      const wrongCredentials = axios.isAxiosError(e) && e.response?.status === 401
      setError(wrongCredentials ? 'Invalid username or password' : 'Could not reach the server')
    }
  }

  return (
    <Box sx={{ display: 'grid', placeItems: 'center', minHeight: '100vh', px: 2 }}>
      <Paper variant="outlined" sx={{ p: 4, width: '100%', maxWidth: 380 }}>
        <Stack component="form" spacing={2} onSubmit={handleSubmit(onSubmit)} noValidate>
          <Typography variant="h5" component="h1">
            Sign in
          </Typography>
          {error && <Alert severity="error">{error}</Alert>}
          <TextField
            label="Username"
            autoComplete="username"
            autoFocus
            {...register('username')}
            error={Boolean(errors.username)}
            helperText={errors.username?.message}
          />
          <TextField
            label="Password"
            type="password"
            autoComplete="current-password"
            {...register('password')}
            error={Boolean(errors.password)}
            helperText={errors.password?.message}
          />
          <Button type="submit" variant="contained" size="large" disabled={isSubmitting}>
            Sign in
          </Button>
        </Stack>
      </Paper>
    </Box>
  )
}
