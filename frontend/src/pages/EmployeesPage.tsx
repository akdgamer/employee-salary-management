import AddIcon from '@mui/icons-material/Add'
import EditIcon from '@mui/icons-material/Edit'
import HistoryIcon from '@mui/icons-material/History'
import PersonOffIcon from '@mui/icons-material/PersonOff'
import PersonIcon from '@mui/icons-material/Person'
import SearchIcon from '@mui/icons-material/Search'
import {
  Box,
  Button,
  Chip,
  InputAdornment,
  MenuItem,
  Paper,
  Stack,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from '@mui/material'
import {
  DataGrid,
  GridActionsCellItem,
  type GridColDef,
  type GridPaginationModel,
  type GridSortModel,
} from '@mui/x-data-grid'
import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { employeesApi, queryKeys } from '@/api/employees'
import type { Employee, EmployeeQuery, EmployeeStatus, SortField } from '@/api/types'
import { ConfirmDialog } from '@/components/ConfirmDialog'
import { EmployeeDialog } from '@/components/employees/EmployeeDialog'
import { SalaryHistoryDrawer } from '@/components/employees/SalaryHistoryDrawer'
import { useDebouncedValue } from '@/hooks/useDebouncedValue'
import { useLookups } from '@/hooks/useLookups'
import { formatDate, formatMoney } from '@/lib/money'

/** Grid columns that the API can sort by, mapped to its sort names. */
const SORTABLE: Record<string, SortField> = {
  full_name: 'name',
  country_code: 'country',
  salary_amount: 'salary',
}

export function EmployeesPage() {
  const queryClient = useQueryClient()
  const { countries, currencies } = useLookups()
  const countryName = useMemo(
    () => Object.fromEntries(countries.map((c) => [c.code, c.name])),
    [countries],
  )

  const [search, setSearch] = useState('')
  const [country, setCountry] = useState('')
  const [status, setStatus] = useState<EmployeeStatus>('active')
  const [pagination, setPagination] = useState<GridPaginationModel>({ page: 0, pageSize: 25 })
  const [sortModel, setSortModel] = useState<GridSortModel>([])
  const debouncedSearch = useDebouncedValue(search.trim())

  const [editing, setEditing] = useState<Employee | 'new' | null>(null)
  const [historyFor, setHistoryFor] = useState<Employee | null>(null)
  const [toggling, setToggling] = useState<Employee | null>(null)

  const sort = sortModel[0]
  const query: EmployeeQuery = {
    search: debouncedSearch || undefined,
    country: country || undefined,
    status,
    sort: sort ? SORTABLE[sort.field] : undefined,
    order: sort?.sort ?? undefined,
    page: pagination.page + 1,
    page_size: pagination.pageSize,
  }
  const { data, isFetching } = useQuery({
    queryKey: queryKeys.employeeList(query),
    queryFn: () => employeesApi.list(query),
    placeholderData: keepPreviousData, // keep rows on screen while the next page loads
  })

  const setActive = useMutation({
    mutationFn: (employee: Employee) =>
      employeesApi.update(employee.id, { is_active: !employee.is_active }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.employees })
      setToggling(null)
    },
  })

  /** Any filter change goes back to the first page; page 7 of old results may not exist. */
  const resetPage = () => setPagination((p) => ({ ...p, page: 0 }))

  const columns: GridColDef<Employee>[] = [
    { field: 'employee_code', headerName: 'Code', width: 120, sortable: false },
    { field: 'full_name', headerName: 'Name', flex: 1, minWidth: 160 },
    { field: 'email', headerName: 'Email', flex: 1.2, minWidth: 200, sortable: false },
    { field: 'job_title', headerName: 'Title', flex: 1, minWidth: 160, sortable: false },
    {
      field: 'country_code',
      headerName: 'Country',
      width: 150,
      valueGetter: (code: string) => countryName[code] ?? code,
    },
    {
      field: 'salary_amount',
      headerName: 'Salary',
      width: 170,
      align: 'right',
      headerAlign: 'right',
      renderCell: ({ row }) => (
        <Box sx={{ lineHeight: 1.3, py: 1 }}>
          <div>{formatMoney(row.salary_amount, row.salary_currency)}</div>
          {row.salary_currency !== 'USD' && (
            <Typography variant="caption" color="text.secondary">
              ≈ {formatMoney(row.salary_usd, 'USD')}
            </Typography>
          )}
        </Box>
      ),
    },
    {
      field: 'is_active',
      headerName: 'Status',
      width: 100,
      sortable: false,
      renderCell: ({ value }) =>
        value ? (
          <Chip label="Active" size="small" color="success" variant="outlined" />
        ) : (
          <Chip label="Inactive" size="small" variant="outlined" />
        ),
    },
    {
      field: 'actions',
      type: 'actions',
      width: 130,
      getActions: ({ row }) => [
        <GridActionsCellItem
          key="edit"
          icon={<EditIcon />}
          label={`Edit ${row.full_name}`}
          onClick={() => setEditing(row)}
        />,
        <GridActionsCellItem
          key="history"
          icon={<HistoryIcon />}
          label={`Salary history for ${row.full_name}`}
          onClick={() => setHistoryFor(row)}
        />,
        <GridActionsCellItem
          key="toggle"
          icon={row.is_active ? <PersonOffIcon /> : <PersonIcon />}
          label={`${row.is_active ? 'Deactivate' : 'Reactivate'} ${row.full_name}`}
          onClick={() => setToggling(row)}
        />,
      ],
    },
  ]

  const ratesAsOf = currencies[0]?.rates_as_of

  return (
    <Stack spacing={2}>
      <Stack direction="row" sx={{ alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h5" component="h1">
          Employees
        </Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setEditing('new')}>
          Add employee
        </Button>
      </Stack>

      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
        <TextField
          size="small"
          placeholder="Search name, email or code"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value)
            resetPage()
          }}
          sx={{ minWidth: 280 }}
          slotProps={{
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" />
                </InputAdornment>
              ),
            },
            htmlInput: { 'aria-label': 'Search employees' },
          }}
        />
        <TextField
          select
          size="small"
          label="Country"
          value={country}
          onChange={(e) => {
            setCountry(e.target.value)
            resetPage()
          }}
          sx={{ minWidth: 200 }}
        >
          <MenuItem value="">All countries</MenuItem>
          {countries.map((c) => (
            <MenuItem key={c.code} value={c.code}>
              {c.name}
            </MenuItem>
          ))}
        </TextField>
        <ToggleButtonGroup
          size="small"
          exclusive
          value={status}
          aria-label="Employee status"
          onChange={(_, value: EmployeeStatus | null) => {
            if (value) {
              setStatus(value)
              resetPage()
            }
          }}
        >
          <ToggleButton value="active">Active</ToggleButton>
          <ToggleButton value="inactive">Inactive</ToggleButton>
          <ToggleButton value="all">All</ToggleButton>
        </ToggleButtonGroup>
      </Stack>

      <Paper variant="outlined" sx={{ height: 640 }}>
        <DataGrid
          rows={data?.items ?? []}
          columns={columns.map((c) => ({ ...c, sortable: c.sortable ?? c.field in SORTABLE }))}
          rowCount={data?.total ?? 0}
          loading={isFetching}
          paginationMode="server"
          sortingMode="server"
          paginationModel={pagination}
          onPaginationModelChange={setPagination}
          pageSizeOptions={[25, 50, 100]}
          sortModel={sortModel}
          onSortModelChange={(model) => {
            setSortModel(model)
            resetPage()
          }}
          rowHeight={56}
          disableRowSelectionOnClick
          disableColumnMenu
        />
      </Paper>

      {ratesAsOf && (
        <Typography variant="caption" color="text.secondary">
          USD amounts use exchange rates as of {formatDate(ratesAsOf)}.
        </Typography>
      )}

      {editing && (
        <EmployeeDialog
          employee={editing === 'new' ? null : editing}
          onClose={() => setEditing(null)}
        />
      )}
      {historyFor && (
        <SalaryHistoryDrawer employee={historyFor} onClose={() => setHistoryFor(null)} />
      )}
      {toggling && (
        <ConfirmDialog
          title={`${toggling.is_active ? 'Deactivate' : 'Reactivate'} ${toggling.full_name}?`}
          message={
            toggling.is_active
              ? 'They will be hidden from the directory and excluded from insights. Their salary history is kept.'
              : 'They will appear in the directory and insights again.'
          }
          confirmLabel={toggling.is_active ? 'Deactivate' : 'Reactivate'}
          pending={setActive.isPending}
          onConfirm={() => setActive.mutate(toggling)}
          onCancel={() => setToggling(null)}
        />
      )}
    </Stack>
  )
}
