import type { MetricCompareItem, QualityFlag, WarningItem } from '@/types/api';

export interface SummaryCard {
  label: string;
  value: string;
  note: string;
}

export function buildWarningSummary(warnings: WarningItem[]): SummaryCard[] {
  const missingCount = warnings.filter((item) => item.warning_type === 'missing').length;
  const abnormalCount = warnings.filter((item) =>
    item.warning_type === 'outlier' || item.warning_type === 'error',
  ).length;
  return [
    { label: '全部预警', value: String(warnings.length), note: '当前筛选范围' },
    { label: '缺失预警', value: String(missingCount), note: '需要补充观测' },
    { label: '异常预警', value: String(abnormalCount), note: '需要重点核验' },
  ];
}

export function sortMetricCompareRows<T extends Pick<MetricCompareItem, 'rank'>>(rows: T[]): T[] {
  return [...rows].sort((a, b) => a.rank - b.rank);
}

export function warningTone(flag: QualityFlag) {
  if (flag === 'missing') {
    return 'warning';
  }
  if (flag === 'outlier' || flag === 'error') {
    return 'error';
  }
  return 'success';
}
