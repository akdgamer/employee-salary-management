/** Money arrives as decimal strings (e.g. "125000.00") to avoid float rounding. */
export type Money = string

export type EmployeeStatus = 'active' | 'inactive' | 'all'
export type SortField = 'name' | 'country' | 'salary'
export type SortOrder = 'asc' | 'desc'

export interface Employee {
  id: number
  employee_code: string
  full_name: string
  email: string
  job_title: string
  country_code: string
  salary_amount: Money
  salary_currency: string
  salary_usd: Money
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface EmployeePage {
  items: Employee[]
  total: number
  page: number
  page_size: number
}

export interface EmployeeQuery {
  search?: string
  country?: string
  status: EmployeeStatus
  sort?: SortField
  order?: SortOrder
  page: number
  page_size: number
}

export interface EmployeeInput {
  full_name: string
  email: string
  job_title: string
  country_code: string
  salary_amount: Money
  salary_currency: string
}

export type EmployeeChanges = Partial<Omit<EmployeeInput, 'salary_currency'>> & {
  is_active?: boolean
}

export interface SalaryChange {
  id: number
  old_amount: Money | null
  new_amount: Money
  currency: string
  changed_at: string
}

export interface Country {
  code: string
  name: string
}

export interface Currency {
  code: string
  name: string
  rate_to_usd: string
  rates_as_of: string
}
