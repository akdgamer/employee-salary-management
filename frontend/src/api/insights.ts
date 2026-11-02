import { api } from './client'
import type { Money } from './types'

/** All insight amounts are USD over active employees. */
export interface CountryPay {
  country_code: string
  country_name: string
  headcount: number
  min_usd: Money
  max_usd: Money
  avg_usd: Money
}

export interface TitlePay {
  job_title: string
  headcount: number
  avg_usd: Money
}

export interface TitleInCountryPay {
  country_code: string
  country_name: string
  headcount: number
  avg_usd: Money
}

export interface Distribution {
  country_code: string
  headcount: number
  p25_usd: Money | null
  p50_usd: Money | null
  p75_usd: Money | null
  p90_usd: Money | null
}

const get = <T>(path: string, params?: Record<string, string>) =>
  api.get<T>(`/insights${path}`, { params }).then((r) => r.data)

export const insightsApi = {
  byCountry: () => get<CountryPay[]>('/by-country'),
  byTitle: (country: string) => get<TitlePay[]>('/by-title', { country }),
  titleComparison: (title: string) => get<TitleInCountryPay[]>('/title-comparison', { title }),
  distribution: (country: string) => get<Distribution>('/distribution', { country }),
  jobTitles: () => get<string[]>('/job-titles'),
}
