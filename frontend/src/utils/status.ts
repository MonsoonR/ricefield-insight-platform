import type { QualityStatus } from '@/types/common';

export type StatusLevel = 'normal' | 'watch' | 'warning' | 'critical' | 'empty';

export interface StatusMeta {
  level: StatusLevel;
  label: string;
  color: string;
  background: string;
  border: string;
}

export const statusLevelMeta: Record<StatusLevel, StatusMeta> = {
  normal: {
    level: 'normal',
    label: '正常',
    color: 'var(--rf-status-normal)',
    background: 'var(--rf-status-normal-bg)',
    border: 'var(--rf-status-normal-line)',
  },
  watch: {
    level: 'watch',
    label: '关注',
    color: 'var(--rf-status-watch)',
    background: 'var(--rf-status-watch-bg)',
    border: 'var(--rf-status-watch-line)',
  },
  warning: {
    level: 'warning',
    label: '预警',
    color: 'var(--rf-status-warning)',
    background: 'var(--rf-status-warning-bg)',
    border: 'var(--rf-status-warning-line)',
  },
  critical: {
    level: 'critical',
    label: '严重',
    color: 'var(--rf-status-critical)',
    background: 'var(--rf-status-critical-bg)',
    border: 'var(--rf-status-critical-line)',
  },
  empty: {
    level: 'empty',
    label: '无数据',
    color: 'var(--rf-status-empty)',
    background: 'var(--rf-status-empty-bg)',
    border: 'var(--rf-status-empty-line)',
  },
};

export function mapQualityToStatus(value?: string | null): StatusLevel {
  switch (value) {
    case 'normal':
    case 'success':
      return 'normal';
    case 'missing':
      return 'watch';
    case 'outlier':
    case 'abnormal':
    case 'warning':
      return 'warning';
    case 'error':
    case 'critical':
      return 'critical';
    case 'empty':
    case 'no_data':
    case '':
    case null:
    case undefined:
      return 'empty';
    default:
      return 'empty';
  }
}

export function statusMetaFromQuality(value?: string | null): StatusMeta {
  return statusLevelMeta[mapQualityToStatus(value)];
}

export const qualityStatusMeta: Record<QualityStatus, { color: string; label: string }> = {
  normal: { color: 'success', label: '正常' },
  abnormal: { color: 'error', label: '预警' },
  missing: { color: 'warning', label: '关注' },
  empty: { color: 'default', label: '无数据' },
};
