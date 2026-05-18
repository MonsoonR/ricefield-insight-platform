export function formatMetricValue(value: number | string | null | undefined, unit = '') {
  if (value === null || value === undefined || value === '') {
    return '无数据';
  }

  return `${value}${unit ? ` ${unit}` : ''}`;
}
