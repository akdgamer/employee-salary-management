import {
  Autocomplete,
  Box,
  MenuItem,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import type { ReactNode } from 'react'
import { insightsApi } from '@/api/insights'
import type { Money } from '@/api/types'
import { RankedBars, type RankedBar } from '@/components/insights/RankedBars'
import { useLookups } from '@/hooks/useLookups'
import { formatDate, formatMoney } from '@/lib/money'

const TOP_TITLES = 5

const usd = (amount: Money | null) => (amount === null ? '—' : formatMoney(amount, 'USD'))

function Section({ title, subtitle, action, children }: {
  title: string
  subtitle?: string
  action?: ReactNode
  children: ReactNode
}) {
  return (
    <Paper variant="outlined" sx={{ p: 2.5 }}>
      <Stack direction="row" sx={{ mb: 2, alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <Box>
          <Typography variant="subtitle1" component="h2" sx={{ fontWeight: 600 }}>
            {title}
          </Typography>
          {subtitle && (
            <Typography variant="body2" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>
        {action}
      </Stack>
      {children}
    </Paper>
  )
}

function StatTile({ label, value }: { label: string; value: string }) {
  return (
    <Paper variant="outlined" sx={{ p: 2, flex: 1, minWidth: 140 }}>
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="h5" component="p" sx={{ fontWeight: 600, mt: 0.5 }}>
        {value}
      </Typography>
    </Paper>
  )
}

function Tip({ heading, lines }: { heading: string; lines: string[] }) {
  return (
    <>
      <Typography variant="body2" sx={{ fontWeight: 600 }}>
        {heading}
      </Typography>
      {lines.map((line) => (
        <Typography key={line} variant="caption" component="div" color="text.secondary">
          {line}
        </Typography>
      ))}
    </>
  )
}

export function InsightsPage() {
  const { currencies } = useLookups()
  const [pickedCountry, setPickedCountry] = useState<string | null>(null)
  const [pickedTitle, setPickedTitle] = useState<string | null>(null)
  const [countryView, setCountryView] = useState<'chart' | 'table'>('chart')

  const byCountry = useQuery({ queryKey: ['insights', 'by-country'], queryFn: insightsApi.byCountry })
  const jobTitles = useQuery({ queryKey: ['insights', 'job-titles'], queryFn: insightsApi.jobTitles })

  const countries = [...(byCountry.data ?? [])].sort((a, b) => Number(b.avg_usd) - Number(a.avg_usd))
  // Default to the country with the most active employees.
  const largest = [...countries].sort((a, b) => b.headcount - a.headcount)[0]?.country_code
  const country = pickedCountry ?? largest ?? null
  const countryName = countries.find((c) => c.country_code === country)?.country_name ?? country
  const title = pickedTitle ?? jobTitles.data?.[0] ?? null

  const distribution = useQuery({
    queryKey: ['insights', 'distribution', country],
    queryFn: () => insightsApi.distribution(country!),
    enabled: country !== null,
  })
  const byTitle = useQuery({
    queryKey: ['insights', 'by-title', country],
    queryFn: () => insightsApi.byTitle(country!),
    enabled: country !== null,
  })
  const comparison = useQuery({
    queryKey: ['insights', 'title-comparison', title],
    queryFn: () => insightsApi.titleComparison(title!),
    enabled: title !== null,
  })

  const ratesAsOf = currencies[0]?.rates_as_of
  const d = distribution.data

  return (
    <Stack spacing={2}>
      <Box>
        <Typography variant="h5" component="h1">
          Insights
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Active employees only · amounts in USD
          {ratesAsOf && ` at exchange rates as of ${formatDate(ratesAsOf)}`}
        </Typography>
      </Box>

      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
        <TextField
          select
          size="small"
          label="Country"
          value={country ?? ''}
          onChange={(e) => setPickedCountry(e.target.value)}
          sx={{ minWidth: 220 }}
        >
          {[...countries]
            .sort((a, b) => a.country_name.localeCompare(b.country_name))
            .map((c) => (
              <MenuItem key={c.country_code} value={c.country_code}>
                {c.country_name}
              </MenuItem>
            ))}
        </TextField>
        <Autocomplete
          size="small"
          options={jobTitles.data ?? []}
          value={title}
          onChange={(_, value) => value && setPickedTitle(value)}
          disableClearable={title !== null}
          sx={{ minWidth: 280 }}
          renderInput={(params) => <TextField {...params} label="Job title" />}
        />
      </Stack>

      <Section title={`Pay distribution in ${countryName ?? '…'}`}>
        <Stack direction="row" useFlexGap spacing={2} sx={{ flexWrap: 'wrap' }}>
          <StatTile label="Employees" value={d ? d.headcount.toLocaleString('en-US') : '—'} />
          <StatTile label="25th percentile" value={d ? usd(d.p25_usd) : '—'} />
          <StatTile label="Median" value={d ? usd(d.p50_usd) : '—'} />
          <StatTile label="75th percentile" value={d ? usd(d.p75_usd) : '—'} />
          <StatTile label="90th percentile" value={d ? usd(d.p90_usd) : '—'} />
        </Stack>
      </Section>

      <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' } }}>
        <Section
          title="Average pay by country"
          subtitle="Highest first · hover for range"
          action={
            <ToggleButtonGroup
              size="small"
              exclusive
              value={countryView}
              onChange={(_, value: 'chart' | 'table' | null) => value && setCountryView(value)}
              aria-label="Country view"
            >
              <ToggleButton value="chart">Chart</ToggleButton>
              <ToggleButton value="table">Table</ToggleButton>
            </ToggleButtonGroup>
          }
        >
          {countryView === 'chart' ? (
            <RankedBars
              ariaLabel="Average pay by country"
              loading={byCountry.isPending}
              bars={countries.map(
                (c): RankedBar => ({
                  key: c.country_code,
                  label: c.country_name,
                  value: Number(c.avg_usd),
                  emphasis: c.country_code === country,
                  tooltip: (
                    <Tip
                      heading={c.country_name}
                      lines={[
                        `Average ${usd(c.avg_usd)}`,
                        `Range ${usd(c.min_usd)} – ${usd(c.max_usd)}`,
                        `${c.headcount.toLocaleString('en-US')} employees`,
                      ]}
                    />
                  ),
                }),
              )}
            />
          ) : (
            <Table size="small" sx={{ '& td, & th': { fontVariantNumeric: 'tabular-nums' } }}>
              <TableHead>
                <TableRow>
                  <TableCell>Country</TableCell>
                  <TableCell align="right">Employees</TableCell>
                  <TableCell align="right">Min</TableCell>
                  <TableCell align="right">Average</TableCell>
                  <TableCell align="right">Max</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {countries.map((c) => (
                  <TableRow key={c.country_code}>
                    <TableCell>{c.country_name}</TableCell>
                    <TableCell align="right">{c.headcount.toLocaleString('en-US')}</TableCell>
                    <TableCell align="right">{usd(c.min_usd)}</TableCell>
                    <TableCell align="right">{usd(c.avg_usd)}</TableCell>
                    <TableCell align="right">{usd(c.max_usd)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </Section>

        <Section
          title={`Average pay by job title in ${countryName ?? '…'}`}
          subtitle={`Top ${TOP_TITLES} highlighted`}
        >
          <RankedBars
            ariaLabel={`Average pay by job title in ${countryName}`}
            loading={byTitle.isPending}
            bars={(byTitle.data ?? []).map(
              (t, rank): RankedBar => ({
                key: t.job_title,
                label: t.job_title,
                value: Number(t.avg_usd),
                emphasis: rank < TOP_TITLES,
                tooltip: (
                  <Tip
                    heading={t.job_title}
                    lines={[`Average ${usd(t.avg_usd)}`, `${t.headcount} employees`]}
                  />
                ),
              }),
            )}
          />
        </Section>
      </Box>

      <Section title={`${title ?? 'Job title'} across countries`} subtitle="Average pay, highest first">
        <RankedBars
          ariaLabel={`Average pay for ${title} by country`}
          loading={comparison.isPending}
          bars={(comparison.data ?? []).map(
            (c): RankedBar => ({
              key: c.country_code,
              label: c.country_name,
              value: Number(c.avg_usd),
              emphasis: true,
              tooltip: (
                <Tip
                  heading={c.country_name}
                  lines={[`Average ${usd(c.avg_usd)}`, `${c.headcount} employees`]}
                />
              ),
            }),
          )}
        />
      </Section>
    </Stack>
  )
}
