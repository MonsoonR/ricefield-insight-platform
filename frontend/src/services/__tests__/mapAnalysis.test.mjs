import assert from 'node:assert/strict';

const mapAnalysis = await import('../mapAnalysis.ts');

assert.equal(mapAnalysis.toApiRegion(undefined), undefined);
assert.equal(mapAnalysis.toApiRegion('all'), undefined);
assert.equal(mapAnalysis.toApiRegion('east'), '试验一区');
assert.equal(mapAnalysis.toApiRegion('west'), '试验二区');

assert.deepEqual(mapAnalysis.buildMapLayerParams({
  region: 'east',
  metricCode: 'chlorophyll',
  observedAt: '2026-05-01',
}), {
  region: '试验一区',
  metric_code: 'chlorophyll',
  observed_at: '2026-05-01',
});

assert.deepEqual(mapAnalysis.buildMapLayerParams({
  region: 'all',
  metricCode: '',
  observedAt: undefined,
}), {});

assert.deepEqual(mapAnalysis.resolvePlotVisualStyle({
  fill_color: '#52C41A',
  quality_flag: 'normal',
  value: 42.6,
}), {
  fillColor: '#52C41A',
  fillOpacity: 0.56,
  outlineColor: '#237804',
  outlineWidth: 1.6,
  dashedOutline: false,
  pulse: false,
  status: 'normal',
});

assert.deepEqual(mapAnalysis.resolvePlotVisualStyle({
  fill_color: '#D9D9D9',
  quality_flag: 'missing',
  value: null,
}), {
  fillColor: '#D9D9D9',
  fillOpacity: 0.32,
  outlineColor: '#8C8C8C',
  outlineWidth: 1.8,
  dashedOutline: true,
  pulse: false,
  status: 'missing',
});

assert.deepEqual(mapAnalysis.resolvePlotVisualStyle({
  fill_color: '#FA8C16',
  quality_flag: 'outlier',
  value: 99,
}), {
  fillColor: '#FA8C16',
  fillOpacity: 0.66,
  outlineColor: '#CF1322',
  outlineWidth: 3,
  dashedOutline: false,
  pulse: true,
  status: 'abnormal',
});

assert.deepEqual(mapAnalysis.resolvePlotVisualStyle({
  fill_color: '#D4380D',
  quality_flag: 'error',
  value: null,
}), {
  fillColor: '#D4380D',
  fillOpacity: 0.66,
  outlineColor: '#CF1322',
  outlineWidth: 3,
  dashedOutline: false,
  pulse: true,
  status: 'abnormal',
});

assert.deepEqual(mapAnalysis.resolvePlotVisualStyle({
  fill_color: '#D9D9D9',
  quality_flag: 'normal',
  status: 'no_data',
  value: 18,
}), {
  fillColor: '#D9D9D9',
  fillOpacity: 0.32,
  outlineColor: '#8C8C8C',
  outlineWidth: 1.8,
  dashedOutline: true,
  pulse: false,
  status: 'missing',
});

assert.deepEqual(mapAnalysis.resolvePlotVisualStyle({
  fill_color: '#52C41A',
  quality_flag: 'normal',
  status: 'duplicate',
  value: 18,
}), {
  fillColor: '#D4380D',
  fillOpacity: 0.66,
  outlineColor: '#CF1322',
  outlineWidth: 3,
  dashedOutline: false,
  pulse: true,
  status: 'abnormal',
});

assert.equal(mapAnalysis.resolvePlotVisualStatus({
  quality_flag: 'missing',
  status: 'normal',
  value: '',
}), 'missing');

assert.equal(mapAnalysis.getMapApiErrorMessage({
  response: {
    data: {
      detail: '未找到指标：unknown_metric',
    },
  },
}, '地图图层加载失败'), '未找到指标：unknown_metric');

assert.equal(
  mapAnalysis.getMapApiErrorMessage(new Error('Network Error'), '地图图层加载失败'),
  '地图图层加载失败',
);

assert.deepEqual(mapAnalysis.trendSeriesForMetric({
  plot: {
    plot_id: 'east-21A',
    plot_code: '21A',
    plot_name: '21A',
    region: '东区',
    status: 'normal',
  },
  series: [
    {
      metric_code: 'chlorophyll',
      metric_name: '叶绿素',
      unit: 'mg/g',
      points: [
        {
          observed_at: '2026-05-03',
          value: 37.1,
          quality_flag: 'normal',
          batch_id: 'batch-2',
          data_source_id: 'source-demo',
        },
        {
          observed_at: '2026-05-01',
          value: 35.8,
          quality_flag: 'normal',
          batch_id: 'batch-1',
          data_source_id: 'source-demo',
        },
      ],
    },
    {
      metric_code: 'nitrogen',
      metric_name: '氮',
      unit: 'mg/kg',
      points: [],
    },
  ],
}, 'chlorophyll')?.points.map((point) => point.observed_at), [
  '2026-05-01',
  '2026-05-03',
]);

assert.equal(mapAnalysis.trendSeriesForMetric({
  plot: {
    plot_id: 'east-21A',
    plot_code: '21A',
    plot_name: '21A',
    region: '东区',
    status: 'normal',
  },
  series: [],
}, 'chlorophyll'), undefined);

console.log('mapAnalysis service tests passed');
