import type { Plot } from '@/types/api';

export interface TwinNavigationItem {
  label: string;
  path: string;
}

export interface PlotDetailRequestPlan {
  routeLocation: {
    name: 'plot-detail';
    params: {
      plotId: string;
    };
  };
  summaryPlotId: string;
  seriesFilters: {
    plotId: string;
  };
}

export interface MapTwinLocation {
  path: '/map-twin';
  query: {
    plotId?: string;
  };
}

export function selectPlotsAfterRegionChange(
  currentPlotIds: string[],
  nextPlots: Pick<Plot, 'plot_id'>[],
  defaultCount = 4,
) {
  const nextPlotIds = new Set(nextPlots.map((plot) => plot.plot_id));
  const preservedPlotIds = currentPlotIds.filter((plotId) => nextPlotIds.has(plotId));
  return preservedPlotIds.length
    ? preservedPlotIds
    : nextPlots.slice(0, defaultCount).map((plot) => plot.plot_id);
}

export function buildPlotDetailRequestPlan(plotId: string): PlotDetailRequestPlan | undefined {
  if (!plotId) {
    return undefined;
  }
  return {
    routeLocation: {
      name: 'plot-detail',
      params: { plotId },
    },
    summaryPlotId: plotId,
    seriesFilters: { plotId },
  };
}

export function shouldReloadPlotDetail(currentPlotId: string, routePlotId: string | string[] | undefined) {
  const nextPlotId = Array.isArray(routePlotId) ? routePlotId[0] : routePlotId;
  return Boolean(nextPlotId && nextPlotId !== currentPlotId);
}

export function buildMapTwinLocation(plotId: string): MapTwinLocation {
  return {
    path: '/map-twin',
    query: plotId ? { plotId } : {},
  };
}

export function firstRouteQueryValue(value: unknown): string {
  if (Array.isArray(value)) {
    return typeof value[0] === 'string' ? value[0] : '';
  }
  return typeof value === 'string' ? value : '';
}

export function buildMetricCompareSeriesFilters(plotIds: string[], metricCode: string | undefined) {
  if (!metricCode) {
    return [];
  }
  return plotIds.map((plotId) => ({
    plotId,
    metricCode,
  }));
}

export function getTwinNavigationItems(): TwinNavigationItem[] {
  return [
    { label: '场景驾驶舱', path: '/overview' },
    { label: 'Cesium 地图孪生', path: '/map-twin' },
    { label: '地块画像', path: '/plot-detail' },
    { label: '指标对比', path: '/metric-compare' },
    { label: '预警分析', path: '/warnings' },
    { label: '系统说明', path: '/system-docs' },
  ];
}
