import { api } from './client'
import type {
  Country,
  Currency,
  Employee,
  EmployeeChanges,
  EmployeeInput,
  EmployeePage,
  EmployeeQuery,
  SalaryChange,
} from './types'

export const employeesApi = {
  list: (query: EmployeeQuery) =>
    api.get<EmployeePage>('/employees', { params: query }).then((r) => r.data),
  create: (input: EmployeeInput) =>
    api.post<Employee>('/employees', input).then((r) => r.data),
  update: (id: number, changes: EmployeeChanges) =>
    api.patch<Employee>(`/employees/${id}`, changes).then((r) => r.data),
  salaryHistory: (id: number) =>
    api.get<SalaryChange[]>(`/employees/${id}/salary-history`).then((r) => r.data),
}

export const lookupsApi = {
  countries: () => api.get<Country[]>('/countries').then((r) => r.data),
  currencies: () => api.get<Currency[]>('/currencies').then((r) => r.data),
}

export const queryKeys = {
  employees: ['employees'] as const,
  employeeList: (query: EmployeeQuery) => ['employees', 'list', query] as const,
  salaryHistory: (id: number) => ['employees', id, 'salary-history'] as const,
  countries: ['countries'] as const,
  currencies: ['currencies'] as const,
}
