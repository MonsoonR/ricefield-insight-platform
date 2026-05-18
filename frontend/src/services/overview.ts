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
  return [
    ...input.stat_cards.map((item: TwinStatCard) => ({
      label: item.label,
      value: item.value,
      note: item.note,
    })),
    {
      label: '孪生健康度',
      value: `${input.health_score}%`,
      note: '按缺失与异常预警估算',
    },
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
