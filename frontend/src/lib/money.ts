const formatters = new Map<string, Intl.NumberFormat>()

/**
 * Format a decimal-string amount in its own currency, e.g. ₹20,00,000 or $125,000.
 * INR uses Indian digit grouping (lakhs and crores), as HR in India reads it.
 */
export function formatMoney(amount: string, currency: string): string {
  let formatter = formatters.get(currency)
  if (!formatter) {
    formatter = new Intl.NumberFormat(currency === 'INR' ? 'en-IN' : 'en-US', {
      style: 'currency',
      currency,
      maximumFractionDigits: 0,
    })
    formatters.set(currency, formatter)
  }
  return formatter.format(Number(amount))
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}
