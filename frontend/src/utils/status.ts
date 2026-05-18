import type { QualityStatus } from '@/types/common';

export const qualityStatusMeta: Record<QualityStatus, { color: string; label: string }> = {
  normal: { color: 'success', label: '正常' },
  abnormal: { color: 'error', label: '异常' },
  missing: { color: 'warning', label: '缺失' },
  empty: { color: 'default', label: '无数据' },
};
