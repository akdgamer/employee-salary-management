import {
  Box,
  CircularProgress,
  Drawer,
  List,
  ListItem,
  ListItemText,
  Typography,
} from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { employeesApi, queryKeys } from '@/api/employees'
import type { Employee } from '@/api/types'
import { formatDate, formatMoney } from '@/lib/money'

export function SalaryHistoryDrawer({
  employee,
  onClose,
}: {
  employee: Employee
  onClose: () => void
}) {
  const { data: history, isLoading } = useQuery({
    queryKey: queryKeys.salaryHistory(employee.id),
    queryFn: () => employeesApi.salaryHistory(employee.id),
  })

  return (
    <Drawer anchor="right" open onClose={onClose}>
      <Box sx={{ width: 360, p: 3 }} role="region" aria-label="Salary history">
        <Typography variant="h6">{employee.full_name}</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Salary history · {employee.employee_code}
        </Typography>
        {isLoading && <CircularProgress size={24} />}
        <List dense disablePadding>
          {history?.map((change) => (
            <ListItem key={change.id} divider disableGutters>
              <ListItemText
                primary={
                  change.old_amount === null
                    ? `Starting salary ${formatMoney(change.new_amount, change.currency)}`
                    : `${formatMoney(change.old_amount, change.currency)} → ${formatMoney(change.new_amount, change.currency)}`
                }
                secondary={formatDate(change.changed_at)}
              />
            </ListItem>
          ))}
        </List>
      </Box>
    </Drawer>
  )
}
