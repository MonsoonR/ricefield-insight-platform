import { createRouter, createWebHistory } from 'vue-router';

import MainLayout from '@/layouts/MainLayout.vue';

export const routes = [
  {
    path: '/',
    component: MainLayout,
    redirect: '/overview',
    children: [
      {
        path: 'overview',
        name: 'overview',
        component: () => import('@/pages/OverviewPage.vue'),
        meta: { title: '场景驾驶舱', subtitle: '稻田数字孪生场景的实时监测与综合状态' },
      },
      {
        path: 'map-twin',
        name: 'map-twin',
        component: () => import('@/pages/MapAnalysisPage.vue'),
        meta: { title: 'Cesium 地图孪生', subtitle: '地块空间分布、指标可视化与交互分析' },
      },
      {
        path: 'metric-compare',
        name: 'metric-compare',
        component: () => import('@/pages/MetricComparePage.vue'),
        meta: { title: '指标对比', subtitle: '多维度指标对比分析，发现地块差异与异常。' },
      },
      {
        path: 'plot-detail/:plotId?',
        name: 'plot-detail',
        component: () => import('@/pages/PlotDetailPage.vue'),
        meta: { title: '地块画像', subtitle: '单个地块的基础信息、趋势与数据来源追溯' },
      },
      {
        path: 'warnings',
        name: 'warnings',
        component: () => import('@/pages/WarningAnalysisPage.vue'),
        meta: { title: '预警分析', subtitle: '识别数据异常与农情风险，辅助科学决策。' },
      },
      {
        path: 'system-docs',
        name: 'system-docs',
        component: () => import('@/pages/SystemDocsPage.vue'),
        meta: { title: '系统说明', subtitle: '平台文档索引、维护提示与协作规范' },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
