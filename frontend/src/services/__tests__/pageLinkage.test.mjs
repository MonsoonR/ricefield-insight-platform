import assert from 'node:assert/strict';

const pageLinkage = await import('../pageLinkage.ts');

const eastPlots = [
  { plot_id: 'east-21A' },
  { plot_id: 'east-22A' },
  { plot_id: 'east-23A' },
  { plot_id: 'east-24A' },
  { plot_id: 'east-25A' },
];
const westPlots = [
  { plot_id: 'west-11B' },
  { plot_id: 'west-12B' },
  { plot_id: 'west-13B' },
  { plot_id: 'west-14B' },
  { plot_id: 'west-15B' },
];

assert.deepEqual(
  pageLinkage.selectPlotsAfterRegionChange(['east-21A', 'east-23A'], eastPlots),
  ['east-21A', 'east-23A'],
  '切换区域后，仍存在于候选列表中的地块选择应保留',
);

assert.deepEqual(
  pageLinkage.selectPlotsAfterRegionChange(['east-21A', 'east-23A'], westPlots),
  ['west-11B', 'west-12B', 'west-13B', 'west-14B'],
  '切换到不包含原地块的区域后，应回退到新候选列表前 4 个地块',
);

assert.deepEqual(
  pageLinkage.buildPlotDetailRequestPlan('west-12B'),
  {
    routeLocation: {
      name: 'plot-detail',
      params: { plotId: 'west-12B' },
    },
    summaryPlotId: 'west-12B',
    seriesFilters: { plotId: 'west-12B' },
  },
  '切换地块后，详情页路由、摘要请求和趋势请求应使用同一个地块 ID',
);

assert.equal(
  pageLinkage.buildPlotDetailRequestPlan(''),
  undefined,
  '未选地块时不应生成详情页请求计划',
);

assert.equal(
  pageLinkage.shouldReloadPlotDetail('east-21A', 'west-12B'),
  true,
  '路由地块 ID 变化时应触发详情刷新',
);

assert.equal(
  pageLinkage.shouldReloadPlotDetail('east-21A', 'east-21A'),
  false,
  '路由地块 ID 未变化时不应重复刷新详情',
);

assert.deepEqual(
  pageLinkage.buildMapTwinLocation('demo-ricefield-2025-A04'),
  {
    path: '/map-twin',
    query: { plotId: 'demo-ricefield-2025-A04' },
  },
  '画像页定位到地图时应携带当前地块 ID 查询参数',
);

assert.deepEqual(
  pageLinkage.buildMapTwinLocation(''),
  {
    path: '/map-twin',
    query: {},
  },
  '未选地块时回到地图不应携带空 plotId',
);

assert.equal(
  pageLinkage.firstRouteQueryValue(['demo-ricefield-2025-B02', 'ignored']),
  'demo-ricefield-2025-B02',
  '地图页应从路由查询参数中读取第一个 plotId',
);

assert.deepEqual(
  pageLinkage.buildMetricCompareSeriesFilters(['east-21A', 'west-12B'], 'chlorophyll'),
  [
    { plotId: 'east-21A', metricCode: 'chlorophyll' },
    { plotId: 'west-12B', metricCode: 'chlorophyll' },
  ],
  '指标对比页应为每个地块生成同一个单选指标的趋势请求参数',
);

assert.deepEqual(
  pageLinkage.buildMetricCompareSeriesFilters(['east-21A'], undefined),
  [],
  '未选择指标时不应发起指标趋势对比请求',
);

assert.deepEqual(
  pageLinkage.getTwinNavigationItems().map((item) => item.label),
  ['场景驾驶舱', 'Cesium 地图孪生', '地块画像', '指标对比', '预警分析', '系统说明'],
  '新版导航应形成六页数字孪生答辩闭环',
);

assert.equal(
  pageLinkage.getTwinNavigationItems().some((item) => item.path.includes('data-import')),
  false,
  '新版导航不应再暴露数据导入中心',
);

console.log('pageLinkage page interaction tests passed');
