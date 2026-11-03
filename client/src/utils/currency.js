// Currency conversion utility
// USD to JPY exchange rate (approximate)
const USD_TO_JPY = 150

export function formatCurrency(amount, currency = 'USD') {
  if (currency === 'JPY') {
    const yenAmount = Math.round(amount * USD_TO_JPY)
    return `¥${yenAmount.toLocaleString('ja-JP')}`
  }
  // Default USD
  return `$${amount.toLocaleString('en-US', { maximumFractionDigits: 0 })}`
}

export function formatCurrencyWithDecimals(amount, currency = 'USD', decimals = 0) {
  if (currency === 'JPY') {
    const yenAmount = Math.round(amount * USD_TO_JPY)
    return `¥${yenAmount.toLocaleString('ja-JP')}`
  }
  // Default USD
  return `$${amount.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}`
}

export function convertAmount(amount, currency = 'USD') {
  if (currency === 'JPY') {
    return Math.round(amount * USD_TO_JPY)
  }
  return amount
}

// Abbreviated amounts for chart axes and KPI cards, e.g. $12K, ¥1.8M
export function formatCompactCurrency(amount, currency = 'USD') {
  const value = Math.abs(convertAmount(amount, currency))
  const sign = amount < 0 ? '-' : ''
  const symbol = currency === 'JPY' ? '¥' : '$'
  const trim = (n) => n.toFixed(1).replace(/\.0$/, '')
  if (value >= 1e9) return `${sign}${symbol}${trim(value / 1e9)}B`
  if (value >= 1e6) return `${sign}${symbol}${trim(value / 1e6)}M`
  if (value >= 1e3) return `${sign}${symbol}${trim(value / 1e3)}K`
  return `${sign}${symbol}${Math.round(value)}`
}
