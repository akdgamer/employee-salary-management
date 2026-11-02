import { zodResolver } from '@hookform/resolvers/zod'
import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Stack,
  TextField,
} from '@mui/material'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { z } from 'zod'
import { employeesApi, queryKeys } from '@/api/employees'
import type { Employee } from '@/api/types'
import { useLookups } from '@/hooks/useLookups'

const schema = z.object({
  full_name: z.string().trim().min(1, 'Required').max(200),
  email: z.email('Enter a valid email'),
  job_title: z.string().trim().min(1, 'Required').max(120),
  country_code: z.string().length(2, 'Choose a country'),
  salary_amount: z
    .string()
    .regex(/^\d{1,12}(\.\d{1,2})?$/, 'Enter an amount like 85000 or 85000.50')
    .refine((value) => Number(value) > 0, 'Must be more than zero'),
  salary_currency: z.string().length(3, 'Choose a currency'),
})
type FormValues = z.infer<typeof schema>

interface Props {
  /** The employee being edited, or null to create a new one. */
  employee: Employee | null
  onClose: () => void
}

export function EmployeeDialog({ employee, onClose }: Props) {
  const isEdit = employee !== null
  const queryClient = useQueryClient()
  const { countries, currencies } = useLookups()
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    setError,
    control,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: employee
      ? {
          full_name: employee.full_name,
          email: employee.email,
          job_title: employee.job_title,
          country_code: employee.country_code,
          salary_amount: employee.salary_amount,
          salary_currency: employee.salary_currency,
        }
      : { country_code: '', salary_currency: '' },
  })

  const save = useMutation({
    mutationFn: ({ salary_currency, ...changes }: FormValues) =>
      isEdit
        ? employeesApi.update(employee.id, changes) // currency is fixed after creation
        : employeesApi.create({ ...changes, salary_currency }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.employees })
      onClose()
    },
    onError: (error) => {
      if (axios.isAxiosError(error) && error.response?.status === 409) {
        setError('email', { message: 'An employee with this email already exists' })
      } else {
        setServerError('Could not save. Please try again.')
      }
    },
  })

  return (
    <Dialog open onClose={onClose} fullWidth maxWidth="sm">
      <form onSubmit={handleSubmit((values) => save.mutate(values))} noValidate>
        <DialogTitle>{isEdit ? `Edit ${employee.employee_code}` : 'Add employee'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            {serverError && <Alert severity="error">{serverError}</Alert>}
            <TextField
              label="Full name"
              {...register('full_name')}
              error={Boolean(errors.full_name)}
              helperText={errors.full_name?.message}
            />
            <TextField
              label="Email"
              type="email"
              {...register('email')}
              error={Boolean(errors.email)}
              helperText={errors.email?.message}
            />
            <TextField
              label="Job title"
              {...register('job_title')}
              error={Boolean(errors.job_title)}
              helperText={errors.job_title?.message}
            />
            <Controller
              name="country_code"
              control={control}
              render={({ field }) => (
                <TextField
                  select
                  label="Country"
                  {...field}
                  error={Boolean(errors.country_code)}
                  helperText={errors.country_code?.message}
                >
                  {countries.map((c) => (
                    <MenuItem key={c.code} value={c.code}>
                      {c.name}
                    </MenuItem>
                  ))}
                </TextField>
              )}
            />
            <Stack direction="row" spacing={2}>
              <TextField
                label="Annual salary"
                inputMode="decimal"
                sx={{ flex: 2 }}
                {...register('salary_amount')}
                error={Boolean(errors.salary_amount)}
                helperText={errors.salary_amount?.message}
              />
              {isEdit ? (
                // Not registered: the currency is fixed after creation and never sent on edit.
                <TextField
                  label="Currency"
                  sx={{ flex: 1 }}
                  value={employee.salary_currency}
                  disabled
                  helperText="Fixed after creation"
                />
              ) : (
                <Controller
                  name="salary_currency"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      select
                      label="Currency"
                      sx={{ flex: 1 }}
                      {...field}
                      error={Boolean(errors.salary_currency)}
                      helperText={errors.salary_currency?.message}
                    >
                      {currencies.map((c) => (
                        <MenuItem key={c.code} value={c.code}>
                          {c.code}
                        </MenuItem>
                      ))}
                    </TextField>
                  )}
                />
              )}
            </Stack>
          </Stack>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained" disabled={save.isPending}>
            {isEdit ? 'Save' : 'Add'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  )
}
