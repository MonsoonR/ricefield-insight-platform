import type { DateRange, ScenarioOverviewResponse, TwinStatCard } from '@/types/api';

interface ApiErrorLike {
  response?: {
    data?: {
      detail?: unknown;
      message?: unknown;
    };
  };
}

export interface OverviewCard {
  label: string;
  value: string;
  note: string;
}

export function buildOverviewCards(input: Pick<ScenarioOverviewResponse, 'stat_cards' | 'health_score'>): OverviewCard[] {
  const cards = input.stat_cards.map((item: TwinStatCard) => ({
      label: item.label,
      value: item.value,
      note: item.note,
    }));
  const order = ['地块数量', '指标数量', '预警数量', '观测天数'];

  return [
    ...cards.sort((left, right) => {
      const leftIndex = order.indexOf(left.label);
      const rightIndex = order.indexOf(right.label);
      return (leftIndex === -1 ? order.length : leftIndex)
        - (rightIndex === -1 ? order.length : rightIndex);
    }),
    {
      label: '孪生健康度',
      value: `${input.health_score}%`,
      note: '按缺失与异常预警估算',
    },
  ];
}

export interface RiskDistributionItem {
  key: 'normal' | 'watch' | 'warning' | 'critical';
  label: string;
  value: number;
}

export function buildRiskDistribution(qualityCounts: Record<string, number>): RiskDistributionItem[] {
  const normal = qualityCounts.normal ?? qualityCounts.success ?? 0;
  const watch = qualityCounts.missing ?? 0;
  const warning = (qualityCounts.outlier ?? 0) + (qualityCounts.abnormal ?? 0) + (qualityCounts.warning ?? 0);
  const critical = qualityCounts.error ?? qualityCounts.critical ?? 0;

  return [
    { key: 'normal', label: '正常', value: normal },
    { key: 'watch', label: '关注', value: watch },
    { key: 'warning', label: '预警', value: warning },
    { key: 'critical', label: '严重', value: critical },
  ];
}

export function formatTwinDateRange(dateRange: DateRange) {
  if (!dateRange.start_date || !dateRange.end_date) {
    return '暂无观测日期';
  }
  return `${dateRange.start_date} 至 ${dateRange.end_date}`;
}

export function getOverviewApiErrorMessage(error: unknown, fallback: string) {
  const apiError = error as ApiErrorLike;
  const detail = apiError.response?.data?.detail ?? apiError.response?.data?.message;
  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }

  return fallback;
}
