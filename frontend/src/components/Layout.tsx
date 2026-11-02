import { AppBar, Box, Button, Container, Toolbar, Typography } from '@mui/material'
import { NavLink, Outlet } from 'react-router'
import { useAuth } from '@/auth/useAuth'

const NAV = [
  { to: '/employees', label: 'Employees' },
  { to: '/insights', label: 'Insights' },
]

export function Layout() {
  const { user, logout } = useAuth()

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="sticky" elevation={0}>
        <Toolbar sx={{ gap: 1 }}>
          <Typography variant="h6" component="span" sx={{ mr: 3, fontWeight: 600 }}>
            Salary Management
          </Typography>
          {NAV.map(({ to, label }) => (
            <Button
              key={to}
              component={NavLink}
              to={to}
              color="inherit"
              sx={{ opacity: 0.8, '&.active': { opacity: 1, fontWeight: 600 } }}
            >
              {label}
            </Button>
          ))}
          <Box sx={{ flexGrow: 1 }} />
          <Typography variant="body2" sx={{ opacity: 0.8 }}>
            {user?.username}
          </Typography>
          <Button color="inherit" onClick={logout}>
            Log out
          </Button>
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Outlet />
      </Container>
    </Box>
  )
}
