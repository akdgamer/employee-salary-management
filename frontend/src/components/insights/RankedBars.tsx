import { Box, CircularProgress, Paper, Typography } from '@mui/material'
import type { ReactNode } from 'react'
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { formatCompactUsd } from '@/lib/money'

export const ACCENT = '#1f4e79'
export const MUTED = '#c3cad3'
const GRID = '#e6e9ee'
const INK_SECONDARY = '#5f6b7a'
const ROW_HEIGHT = 30

export interface RankedBar {
  key: string
  label: string
  value: number
  /** Accent bars carry the story; the rest are grey context. */
  emphasis: boolean
  tooltip: ReactNode
}

/** Horizontal bars sorted by the caller, one hue (no legend), value in the tooltip. */
export function RankedBars({
  bars,
  ariaLabel,
  loading,
}: {
  bars: RankedBar[]
  ariaLabel: string
  loading: boolean
}) {
  if (loading) {
    return (
      <Box sx={{ display: 'grid', placeItems: 'center', py: 4 }}>
        <CircularProgress size={24} aria-label={`Loading ${ariaLabel.toLowerCase()}`} />
      </Box>
    )
  }
  if (bars.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
        No active employees
      </Typography>
    )
  }

  return (
    <Box role="img" aria-label={ariaLabel} sx={{ height: bars.length * ROW_HEIGHT + 40 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={bars} layout="vertical" margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
          <CartesianGrid horizontal={false} stroke={GRID} />
          <XAxis
            type="number"
            tickFormatter={formatCompactUsd}
            tick={{ fill: INK_SECONDARY, fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="label"
            width={170}
            tick={{ fill: INK_SECONDARY, fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            cursor={{ fill: 'rgba(31, 78, 121, 0.06)' }}
            content={({ active, payload }) =>
              active && payload?.[0] ? (
                <Paper variant="outlined" sx={{ px: 1.5, py: 1 }}>
                  {(payload[0].payload as RankedBar).tooltip}
                </Paper>
              ) : null
            }
          />
          <Bar dataKey="value" barSize={16} radius={[0, 4, 4, 0]} isAnimationActive={false}>
            {bars.map((bar) => (
              <Cell key={bar.key} fill={bar.emphasis ? ACCENT : MUTED} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Box>
  )
}
