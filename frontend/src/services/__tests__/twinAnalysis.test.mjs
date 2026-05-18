import assert from 'node:assert/strict';

const twinAnalysis = await import('../twinAnalysis.ts');

const warnings = [
  {
    warning_id: 'w1',
    scenario_id: 'demo-ricefield-2025',
    warning_type: 'missing',
    severity: 'warning',
    plot_id: 'A03',
    plot_code: 'A03',
    region: '试验一区',
    metric_code: 'crop_growth',
    metric_name: '作物长势',
    observed_at: '2025-07-15',
    value: null,
    message: '缺失',
  },
  {
    warning_id: 'w2',
    scenario_id: 'demo-ricefield-2025',
    warning_type: 'outlier',
    severity: 'error',
    plot_id: 'B04',
    plot_code: 'B04',
    region: '试验二区',
    metric_code: 'crop_growth',
    metric_name: '作物长势',
    observed_at: '2025-07-15',
    value: 1.22,
    message: '异常',
  },
];

assert.deepEqual(twinAnalysis.buildWarningSummary(warnings), [
  { label: '全部预警', value: '2', note: '当前筛选范围' },
  { label: '缺失预警', value: '1', note: '需要补充观测' },
  { label: '异常预警', value: '1', note: '需要重点核验' },
]);

assert.deepEqual(twinAnalysis.sortMetricCompareRows([
  { rank: 2, plot_code: 'A02', value: 0.7 },
  { rank: 1, plot_code: 'A01', value: 0.9 },
]), [
  { rank: 1, plot_code: 'A01', value: 0.9 },
  { rank: 2, plot_code: 'A02', value: 0.7 },
]);

assert.equal(twinAnalysis.warningTone('missing'), 'warning');
assert.equal(twinAnalysis.warningTone('outlier'), 'error');
assert.equal(twinAnalysis.warningTone('normal'), 'success');

console.log('twinAnalysis service tests passed');
