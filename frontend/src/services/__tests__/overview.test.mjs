import assert from 'node:assert/strict';

const overview = await import('../overview.ts');

const cards = overview.buildOverviewCards({
  stat_cards: [
    { label: '地块数量', value: '8', note: '程序生成示例地块' },
    { label: '指标数量', value: '11', note: '数字孪生指标字典' },
    { label: '观测天数', value: '45', note: '2025-06-01 至 2025-07-15' },
    { label: '预警数量', value: '6', note: '缺失、异常和突变提示' },
  ],
  health_score: 92,
});

assert.deepEqual(cards, [
  { label: '地块数量', value: '8', note: '程序生成示例地块' },
  { label: '指标数量', value: '11', note: '数字孪生指标字典' },
  { label: '预警数量', value: '6', note: '缺失、异常和突变提示' },
  { label: '观测天数', value: '45', note: '2025-06-01 至 2025-07-15' },
  { label: '孪生健康度', value: '92%', note: '按缺失与异常预警估算' },
]);

assert.deepEqual(overview.buildRiskDistribution({
  normal: 3954,
  missing: 2,
  outlier: 4,
  error: 1,
}), [
  { key: 'normal', label: '正常', value: 3954 },
  { key: 'watch', label: '关注', value: 2 },
  { key: 'warning', label: '预警', value: 4 },
  { key: 'critical', label: '严重', value: 1 },
]);

assert.equal(overview.formatTwinDateRange({
  start_date: '2025-06-01',
  end_date: '2025-07-15',
}), '2025-06-01 至 2025-07-15');

assert.equal(overview.formatTwinDateRange({
  start_date: null,
  end_date: null,
}), '暂无观测日期');

assert.equal(overview.getOverviewApiErrorMessage({
  response: {
    data: {
      detail: '未找到场景：unknown',
    },
  },
}, '场景驾驶舱加载失败'), '未找到场景：unknown');

console.log('overview service tests passed');
