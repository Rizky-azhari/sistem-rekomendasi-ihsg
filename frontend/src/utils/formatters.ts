/**
 * Format a number to Indonesian Rupiah (IDR) currency string.
 */
export function formatIDR(value: number): string {
  return `Rp ${value?.toLocaleString('id-ID') || 0}`;
}

/**
 * Format a date string (YYYY-MM-DD) to Indonesian locale (DD MMM YYYY).
 */
export function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('id-ID', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

/**
 * Format large volume numbers to human-readable format (e.g., 1.5M, 200K).
 */
export function formatVolume(vol: number): string {
  if (vol >= 1_000_000_000) return `${(vol / 1_000_000_000).toFixed(1)}B`;
  if (vol >= 1_000_000) return `${(vol / 1_000_000).toFixed(1)}M`;
  if (vol >= 1_000) return `${(vol / 1_000).toFixed(1)}K`;
  return vol.toString();
}
