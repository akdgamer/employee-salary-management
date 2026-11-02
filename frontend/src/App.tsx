import { Box, CircularProgress } from '@mui/material'
import { Suspense, lazy } from 'react'
import { Navigate, Route, Routes } from 'react-router'
import { ProtectedRoute } from '@/auth/ProtectedRoute'
import { Layout } from '@/components/Layout'
import { LoginPage } from '@/pages/LoginPage'

// Loaded on demand so the sign-in page doesn't download the data grid and charts.
const EmployeesPage = lazy(() =>
  import('@/pages/EmployeesPage').then((m) => ({ default: m.EmployeesPage })),
)
const InsightsPage = lazy(() =>
  import('@/pages/InsightsPage').then((m) => ({ default: m.InsightsPage })),
)

function PageLoading() {
  return (
    <Box sx={{ display: 'grid', placeItems: 'center', py: 8 }}>
      <CircularProgress aria-label="Loading page" />
    </Box>
  )
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route
            path="/employees"
            element={
              <Suspense fallback={<PageLoading />}>
                <EmployeesPage />
              </Suspense>
            }
          />
          <Route
            path="/insights"
            element={
              <Suspense fallback={<PageLoading />}>
                <InsightsPage />
              </Suspense>
            }
          />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/employees" replace />} />
    </Routes>
  )
}
