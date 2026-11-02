import { useQuery } from '@tanstack/react-query'
import { lookupsApi, queryKeys } from '@/api/employees'

/** Countries and currencies change only on re-seed, so they are fetched once per session. */
export function useLookups() {
  const countries = useQuery({
    queryKey: queryKeys.countries,
    queryFn: lookupsApi.countries,
    staleTime: Infinity,
  })
  const currencies = useQuery({
    queryKey: queryKeys.currencies,
    queryFn: lookupsApi.currencies,
    staleTime: Infinity,
  })
  return { countries: countries.data ?? [], currencies: currencies.data ?? [] }
}
