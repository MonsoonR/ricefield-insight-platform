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
        meta: { title: '场景驾驶舱' },
      },
      {
        path: 'map-twin',
        name: 'map-twin',
        component: () => import('@/pages/MapAnalysisPage.vue'),
        meta: { title: 'Cesium 地图孪生' },
      },
      {
        path: 'metric-compare',
        name: 'metric-compare',
        component: () => import('@/pages/MetricComparePage.vue'),
        meta: { title: '指标对比' },
      },
      {
        path: 'plot-detail/:plotId?',
        name: 'plot-detail',
        component: () => import('@/pages/PlotDetailPage.vue'),
        meta: { title: '地块详情' },
      },
      {
        path: 'warnings',
        name: 'warnings',
        component: () => import('@/pages/WarningAnalysisPage.vue'),
        meta: { title: '预警分析' },
      },
      {
        path: 'system-docs',
        name: 'system-docs',
        component: () => import('@/pages/SystemDocsPage.vue'),
        meta: { title: '系统文档' },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
