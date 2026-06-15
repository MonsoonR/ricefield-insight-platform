<template>
  <section class="map-panel">
    <header v-if="title || $slots.toolbar" class="map-panel__header">
      <div>
        <h2>{{ title }}</h2>
        <p>{{ featureCount }} 个地块 · 卫星底图 + 地块指标图层</p>
      </div>
      <slot name="toolbar" />
    </header>
    <div class="map-panel__canvas" :style="{ height: `${height}px`, minHeight: `${height}px` }">
      <div ref="containerRef" class="map-panel__cesium" />
      <div v-if="$slots.filters" class="map-panel__filters">
        <slot name="filters" />
      </div>
      <div class="map-panel__tools map-panel__tools--left">
        <button type="button" title="定位选中地块" @click="locateSelectedPlot">
          <AimOutlined />
        </button>
        <button type="button" title="图层透明度" @click="toggleAlpha">
          <AppstoreOutlined />
        </button>
        <button type="button" title="回到默认视角" @click="zoomHome">
          <HomeOutlined />
        </button>
      </div>
      <div class="map-panel__tools map-panel__tools--right">
        <button type="button" title="放大" @click="zoomIn">
          <PlusOutlined />
        </button>
        <button type="button" title="缩小" @click="zoomOut">
          <MinusOutlined />
        </button>
      </div>
      <div v-if="imageryError" class="map-panel__notice map-panel__notice--error">
        {{ imageryError }}
      </div>
      <div v-else-if="loading" class="map-panel__notice">正在加载地图图层...</div>
      <div v-if="empty" class="map-panel__empty">暂无可展示地块</div>
      <div v-if="$slots.legend" class="map-panel__legend">
        <slot name="legend" />
      </div>
      <div class="map-panel__scale">100 m</div>
    </div>
  </section>
</template>

<script setup lang="ts">
import {
  Crosshair as AimOutlined,
  Home as HomeOutlined,
  Layers as AppstoreOutlined,
  Minus as MinusOutlined,
  Plus as PlusOutlined,
} from 'lucide-vue-next';
import {
  Cartographic,
  Cartesian2,
  Cartesian3,
  Color,
  ColorMaterialProperty,
  ConstantProperty,
  GeoJsonDataSource,
  HorizontalOrigin,
  Ion,
  IonWorldImageryStyle,
  LabelStyle,
  Math as CesiumMath,
  PolylineDashMaterialProperty,
  ScreenSpaceEventHandler,
  ScreenSpaceEventType,
  UrlTemplateImageryProvider,
  VerticalOrigin,
  Viewer,
  createWorldImageryAsync,
  type Entity,
} from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css';
import { computed, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue';

import {
  resolvePlotVisualStatus,
  resolvePlotVisualStyle,
  type MapFeatureCollection,
  type MapFeatureProperties,
} from '@/services/mapAnalysis';

const props = withDefaults(
  defineProps<{
    title?: string;
    height?: number;
    featureCollection: MapFeatureCollection;
    loading?: boolean;
    selectedPlotId?: string;
    showBoundaries?: boolean;
    showMetricLayer?: boolean;
    showWarnings?: boolean;
    showRegionBoundary?: boolean;
    tightView?: boolean;
  }>(),
  {
    title: '',
    height: 520,
    loading: false,
    selectedPlotId: undefined,
    showBoundaries: true,
    showMetricLayer: true,
    showWarnings: true,
    showRegionBoundary: false,
    tightView: false,
  },
);

const emit = defineEmits<{
  'plot-click': [properties: MapFeatureProperties];
  'imagery-error': [message: string];
}>();

const containerRef = ref<HTMLDivElement>();
const viewer = shallowRef<Viewer>();
const dataSource = shallowRef<GeoJsonDataSource>();
const imageryError = ref('');
const polygonAlpha = ref(0.74);
const outlineEntities: Entity[] = [];
const labelEntities: Entity[] = [];
const regionBoundaryEntities: Entity[] = [];
let clickHandler: ScreenSpaceEventHandler | undefined;
let renderRequestId = 0;
let resizeObserver: ResizeObserver | undefined;
let resizeFrameId = 0;

const featureCount = computed(() => props.featureCollection.features.length);
const empty = computed(() => !props.loading && featureCount.value === 0);

onMounted(async () => {
  if (!containerRef.value) {
    return;
  }

  const token = import.meta.env.VITE_CESIUM_ION_TOKEN as string | undefined;
  if (token) {
    Ion.defaultAccessToken = token;
  }

  viewer.value = new Viewer(containerRef.value, {
    animation: false,
    baseLayer: false,
    baseLayerPicker: false,
    fullscreenButton: false,
    geocoder: false,
    homeButton: false,
    infoBox: false,
    navigationHelpButton: false,
    sceneModePicker: false,
    selectionIndicator: false,
    skyAtmosphere: false,
    skyBox: false,
    timeline: false,
  });

  viewer.value.scene.globe.baseColor = Color.fromCssColorString('#1e3a2b');
  viewer.value.scene.screenSpaceCameraController.enableTilt = false;
  viewer.value.scene.screenSpaceCameraController.enableRotate = true;
  resizeObserver = new ResizeObserver(() => {
    scheduleViewerResize();
  });
  resizeObserver.observe(containerRef.value);

  await setupImageryLayer();
  scheduleViewerResize();

  clickHandler = new ScreenSpaceEventHandler(viewer.value.scene.canvas);
  clickHandler.setInputAction((movement: ScreenSpaceEventHandler.PositionedEvent) => {
    selectFeatureAtPosition(movement.position);
  }, ScreenSpaceEventType.LEFT_CLICK);

  void renderGeoJson();
});

onBeforeUnmount(() => {
  renderRequestId += 1;
  resizeObserver?.disconnect();
  resizeObserver = undefined;
  if (resizeFrameId) {
    window.cancelAnimationFrame(resizeFrameId);
    resizeFrameId = 0;
  }
  clearDataSource();
  clickHandler?.destroy();
  if (viewer.value && !viewer.value.isDestroyed()) {
    viewer.value.destroy();
  }
  viewer.value = undefined;
});

watch(
  () => props.featureCollection,
  () => {
    void renderGeoJson();
  },
);

watch(
  () => props.height,
  () => {
    scheduleViewerResize();
  },
);

watch(
  () => [
    props.selectedPlotId,
    props.showBoundaries,
    props.showMetricLayer,
    props.showWarnings,
    props.showRegionBoundary,
  ],
  () => {
    applyEntityStyles();
    renderMapOverlays();
  },
);

async function setupImageryLayer() {
  if (!viewer.value || viewer.value.isDestroyed()) {
    return;
  }

  try {
    const token = import.meta.env.VITE_CESIUM_ION_TOKEN as string | undefined;
    const fallbackUrl = import.meta.env.VITE_CESIUM_IMAGERY_URL as string | undefined;
    const publicSatelliteUrl = 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
    const provider = fallbackUrl
      ? new UrlTemplateImageryProvider({ url: fallbackUrl, enablePickFeatures: false })
      : token
        ? await createWorldImageryAsync({ style: IonWorldImageryStyle.AERIAL })
        : new UrlTemplateImageryProvider({ url: publicSatelliteUrl, enablePickFeatures: false });

    viewer.value.imageryLayers.removeAll();
    viewer.value.imageryLayers.addImageryProvider(provider);
    imageryError.value = '';
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    imageryError.value = `卫星底图加载失败，请检查 VITE_CESIUM_ION_TOKEN 或 VITE_CESIUM_IMAGERY_URL 配置。（${message}）`;
    emit('imagery-error', imageryError.value);
  }
}

async function renderGeoJson() {
  const currentViewer = viewer.value;
  if (!currentViewer || currentViewer.isDestroyed()) {
    return;
  }
  const requestId = ++renderRequestId;

  clearDataSource();

  if (!props.featureCollection.features.length) {
    return;
  }

  try {
    const nextDataSource = await GeoJsonDataSource.load(props.featureCollection, {
      clampToGround: false,
    });
    if (requestId !== renderRequestId || !viewer.value || viewer.value.isDestroyed()) {
      return;
    }

    dataSource.value = nextDataSource;
    viewer.value.dataSources.add(nextDataSource);
    scheduleViewerResize();
    applyEntityStyles();
    renderMapOverlays();
    await zoomToDataSource(nextDataSource);
  } catch {
    imageryError.value = '地块图层加载失败，请检查 /api/map/layers 返回的 GeoJSON 结构。';
  }
}

function applyEntityStyles() {
  const currentDataSource = dataSource.value;
  if (!currentDataSource) {
    return;
  }

  currentDataSource.entities.values.forEach((entity) => {
    const properties = getEntityProperties(entity);
    const polygon = entity.polygon;
    if (!properties || !polygon) {
      return;
    }

    const style = resolvePlotVisualStyle(properties);
    const visualStatus = resolvePlotVisualStatus(properties);
    const isSelected = properties.plot_id === props.selectedPlotId;
    const warningMuted = visualStatus === 'abnormal' && !props.showWarnings;
    const baseAlpha = props.showMetricLayer ? style.fillOpacity : 0.08;
    const alpha = warningMuted
      ? 0.16
      : Math.min(Math.max(baseAlpha * polygonAlpha.value + (isSelected ? 0.18 : 0), 0.08), 0.66);

    polygon.material = new ColorMaterialProperty(
      Color.fromCssColorString(warningMuted ? '#d1d5db' : style.fillColor).withAlpha(alpha),
    );
    polygon.outline = new ConstantProperty(false);
  });
}

function renderMapOverlays() {
  renderOutlines();
  renderPlotLabels();
  renderRegionBoundaries();
}

function renderOutlines() {
  if (!viewer.value) {
    return;
  }

  clearOutlines();

  if (!props.showBoundaries) {
    return;
  }

  props.featureCollection.features.forEach((feature) => {
    const style = resolvePlotVisualStyle(feature.properties);
    const isSelected = feature.properties.plot_id === props.selectedPlotId;
    const visualStatus = resolvePlotVisualStatus(feature.properties);
    const warningMuted = visualStatus === 'abnormal' && !props.showWarnings;
    const rings = getOuterRings(feature.geometry);

    rings.forEach((ring) => {
      const positions = Cartesian3.fromDegreesArray(ring.flatMap(([lng, lat]) => [lng, lat]));
      if (isSelected || (style.pulse && !warningMuted)) {
        const glow = viewer.value?.entities.add({
          properties: feature.properties,
          polyline: {
            positions,
            clampToGround: new ConstantProperty(true),
            width: isSelected ? 8 : 5,
            material: new ColorMaterialProperty(
              Color.fromCssColorString(isSelected ? '#f97316' : style.outlineColor).withAlpha(0.26),
            ),
          },
        });
        if (glow) {
          outlineEntities.push(glow);
        }
      }

      const outline = viewer.value?.entities.add({
        properties: feature.properties,
        polyline: {
          positions,
          clampToGround: new ConstantProperty(true),
          width: style.outlineWidth + (isSelected ? 2 : 0),
          material: style.dashedOutline && !isSelected
            ? new PolylineDashMaterialProperty({
                color: Color.fromCssColorString(style.outlineColor).withAlpha(0.96),
                dashLength: 14,
              })
            : new ColorMaterialProperty(
                Color.fromCssColorString(isSelected ? '#fff7ed' : warningMuted ? '#9ca3af' : style.outlineColor)
                  .withAlpha(isSelected ? 1 : 0.92),
              ),
        },
      });

      if (outline) {
        outlineEntities.push(outline);
      }
    });
  });
}

function renderPlotLabels() {
  if (!viewer.value) {
    return;
  }

  clearLabels();

  props.featureCollection.features.forEach((feature) => {
    const center = getFeatureCenter(feature.geometry);
    const label = feature.properties.plot_code || feature.properties.plot_id;
    if (!center || !label) {
      return;
    }

    const entity = viewer.value?.entities.add({
      properties: feature.properties,
      position: Cartesian3.fromDegrees(center[0], center[1], 8),
      label: {
        text: String(label),
        font: '700 15px "Microsoft YaHei", sans-serif',
        fillColor: Color.WHITE,
        outlineColor: Color.fromCssColorString('#10291f'),
        outlineWidth: 4,
        style: LabelStyle.FILL_AND_OUTLINE,
        horizontalOrigin: HorizontalOrigin.CENTER,
        verticalOrigin: VerticalOrigin.CENTER,
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
      },
    });

    if (entity) {
      labelEntities.push(entity);
    }
  });
}

function renderRegionBoundaries() {
  if (!viewer.value) {
    return;
  }

  clearRegionBoundaries();

  if (!props.showRegionBoundary) {
    return;
  }

  const regionBounds = new Map<string, { west: number; south: number; east: number; north: number }>();
  props.featureCollection.features.forEach((feature) => {
    const region = feature.properties.region || '全部区域';
    getOuterRings(feature.geometry).flat().forEach(([lng, lat]) => {
      const bounds = regionBounds.get(region) ?? { west: lng, south: lat, east: lng, north: lat };
      bounds.west = Math.min(bounds.west, lng);
      bounds.south = Math.min(bounds.south, lat);
      bounds.east = Math.max(bounds.east, lng);
      bounds.north = Math.max(bounds.north, lat);
      regionBounds.set(region, bounds);
    });
  });

  regionBounds.forEach((bounds, region) => {
    const paddingLng = (bounds.east - bounds.west) * 0.12;
    const paddingLat = (bounds.north - bounds.south) * 0.18;
    const ring: Array<[number, number]> = [
      [bounds.west - paddingLng, bounds.south - paddingLat],
      [bounds.east + paddingLng, bounds.south - paddingLat],
      [bounds.east + paddingLng, bounds.north + paddingLat],
      [bounds.west - paddingLng, bounds.north + paddingLat],
      [bounds.west - paddingLng, bounds.south - paddingLat],
    ];
    const positions = Cartesian3.fromDegreesArray(ring.flatMap(([lng, lat]) => [lng, lat]));
    const outline = viewer.value?.entities.add({
      name: region,
      polyline: {
        positions,
        clampToGround: new ConstantProperty(true),
        width: 2,
        material: new PolylineDashMaterialProperty({
          color: Color.fromCssColorString('#38bdf8').withAlpha(0.92),
          dashLength: 20,
        }),
      },
    });
    if (outline) {
      regionBoundaryEntities.push(outline);
    }
  });
}

function clearOutlines() {
  if (!viewer.value || viewer.value.isDestroyed()) {
    outlineEntities.length = 0;
    return;
  }

  outlineEntities.splice(0).forEach((entity) => viewer.value?.entities.remove(entity));
}

function clearLabels() {
  if (!viewer.value || viewer.value.isDestroyed()) {
    labelEntities.length = 0;
    return;
  }

  labelEntities.splice(0).forEach((entity) => viewer.value?.entities.remove(entity));
}

function clearRegionBoundaries() {
  if (!viewer.value || viewer.value.isDestroyed()) {
    regionBoundaryEntities.length = 0;
    return;
  }

  regionBoundaryEntities.splice(0).forEach((entity) => viewer.value?.entities.remove(entity));
}

function clearDataSource() {
  clearOutlines();
  clearLabels();
  clearRegionBoundaries();

  if (dataSource.value && viewer.value && !viewer.value.isDestroyed()) {
    viewer.value.dataSources.remove(dataSource.value, true);
  }
  dataSource.value = undefined;
}

function getEntityProperties(entity: Entity | undefined): MapFeatureProperties | undefined {
  const rawProperties = entity?.properties;
  if (!rawProperties) {
    return undefined;
  }

  if ('getValue' in rawProperties) {
    return rawProperties.getValue(viewer.value?.clock.currentTime) as MapFeatureProperties;
  }

  return rawProperties as unknown as MapFeatureProperties;
}

function selectFeatureAtPosition(position: Cartesian2) {
  const pickedItems = viewer.value?.scene.drillPick(position) ?? [];
  const pickedEntity = pickedItems
    .map((item) => (item.id ?? item.primitive?.id) as Entity | undefined)
    .find((entity) => Boolean(getEntityProperties(entity)?.plot_id));
  const properties = getEntityProperties(pickedEntity) ?? getFeaturePropertiesAtPosition(position);

  if (properties?.plot_id) {
    emit('plot-click', properties);
  }
}

function getOuterRings(geometry: MapFeatureCollection['features'][number]['geometry']) {
  if (geometry.type === 'Polygon' && Array.isArray(geometry.coordinates)) {
    const ring = geometry.coordinates[0];
    return isRing(ring) ? [ring] : [];
  }

  if (geometry.type === 'MultiPolygon' && Array.isArray(geometry.coordinates)) {
    return geometry.coordinates
      .map((polygon) => (Array.isArray(polygon) ? polygon[0] : undefined))
      .filter(isRing);
  }

  return [];
}

function getFeatureCenter(geometry: MapFeatureCollection['features'][number]['geometry']) {
  const ring = getOuterRings(geometry)[0];
  if (!ring?.length) {
    return undefined;
  }

  let area = 0;
  let lngSum = 0;
  let latSum = 0;
  for (let i = 0; i < ring.length - 1; i += 1) {
    const [lngA, latA] = ring[i];
    const [lngB, latB] = ring[i + 1];
    const factor = lngA * latB - lngB * latA;
    area += factor;
    lngSum += (lngA + lngB) * factor;
    latSum += (latA + latB) * factor;
  }

  if (Math.abs(area) > 0.0000001) {
    return [lngSum / (3 * area), latSum / (3 * area)] as [number, number];
  }

  const totals = ring.reduce(
    (acc, [lng, lat]) => ({ lng: acc.lng + lng, lat: acc.lat + lat }),
    { lng: 0, lat: 0 },
  );
  return [totals.lng / ring.length, totals.lat / ring.length] as [number, number];
}

function isRing(value: unknown): value is Array<[number, number]> {
  return Array.isArray(value) && value.every(
    (position) =>
      Array.isArray(position)
      && typeof position[0] === 'number'
      && typeof position[1] === 'number',
  );
}

function getFeaturePropertiesAtPosition(position: ScreenSpaceEventHandler.PositionedEvent['position']) {
  if (!viewer.value) {
    return undefined;
  }

  const cartesian = viewer.value.scene.camera.pickEllipsoid(
    position,
    viewer.value.scene.globe.ellipsoid,
  );
  if (!cartesian) {
    return undefined;
  }

  const cartographic = Cartographic.fromCartesian(cartesian);
  const point: [number, number] = [
    CesiumMath.toDegrees(cartographic.longitude),
    CesiumMath.toDegrees(cartographic.latitude),
  ];

  return props.featureCollection.features.find((feature) =>
    getOuterRings(feature.geometry).some((ring) => pointInRing(point, ring)),
  )?.properties;
}

function pointInRing(point: [number, number], ring: Array<[number, number]>) {
  const [lng, lat] = point;
  let inside = false;

  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [lngI, latI] = ring[i];
    const [lngJ, latJ] = ring[j];
    const intersects = (latI > lat) !== (latJ > lat)
      && lng < ((lngJ - lngI) * (lat - latI)) / (latJ - latI) + lngI;

    if (intersects) {
      inside = !inside;
    }
  }

  return inside;
}

function zoomHome() {
  if (dataSource.value) {
    void zoomToDataSource(dataSource.value);
  }
}

function scheduleViewerResize() {
  if (resizeFrameId) {
    window.cancelAnimationFrame(resizeFrameId);
  }
  resizeFrameId = window.requestAnimationFrame(() => {
    resizeFrameId = 0;
    const currentViewer = viewer.value;
    if (!currentViewer || currentViewer.isDestroyed()) {
      return;
    }
    currentViewer.forceResize();
  });
}

async function zoomToDataSource(nextDataSource: GeoJsonDataSource) {
  const currentViewer = viewer.value;
  if (!currentViewer || currentViewer.isDestroyed()) {
    return;
  }

  await currentViewer.zoomTo(nextDataSource);
  if (!props.tightView) {
    return;
  }

  const height = currentViewer.camera.positionCartographic.height;
  currentViewer.camera.zoomIn(Math.max(height * 0.56, 1));
}

function locateSelectedPlot() {
  if (!viewer.value || !props.selectedPlotId) {
    zoomHome();
    return;
  }

  const target = dataSource.value?.entities.values.find((entity) =>
    getEntityProperties(entity)?.plot_id === props.selectedPlotId,
  );
  if (target) {
    void viewer.value.flyTo(target, { duration: 0.8 });
  } else {
    zoomHome();
  }
}

function zoomIn() {
  viewer.value?.camera.zoomIn();
}

function zoomOut() {
  viewer.value?.camera.zoomOut();
}

function toggleAlpha() {
  polygonAlpha.value = polygonAlpha.value > 0.72 ? 0.52 : 0.78;
  applyEntityStyles();
}
</script>

<style scoped>
.map-panel {
  overflow: hidden;
  border: 1px solid rgba(12, 45, 33, 0.12);
  border-radius: var(--rf-radius-lg);
  background: #0f2b22;
  box-shadow: 0 18px 42px rgba(6, 74, 51, 0.16);
}

.map-panel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  border-bottom: 1px solid rgba(237, 242, 239, 0.86);
  background: #fff;
  padding: 16px 18px;
}

.map-panel__header h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 850;
}

.map-panel__header p {
  margin: 4px 0 0;
  color: var(--rf-text-muted);
  font-size: 12px;
}

.map-panel__canvas {
  position: relative;
  overflow: hidden;
  min-width: 0;
  background: #10291f;
}

.map-panel__canvas::after {
  position: absolute;
  inset: 0;
  pointer-events: none;
  content: "";
  background:
    linear-gradient(180deg, rgba(8, 28, 21, 0.42), rgba(8, 28, 21, 0.03) 34%, rgba(8, 28, 21, 0.18)),
    radial-gradient(circle at 50% 42%, transparent 0 55%, rgba(8, 24, 18, 0.22) 100%);
  z-index: 1;
}

.map-panel__cesium {
  position: absolute;
  inset: 0;
}

.map-panel__cesium :deep(.cesium-viewer),
.map-panel__cesium :deep(.cesium-viewer-cesiumWidgetContainer),
.map-panel__cesium :deep(.cesium-widget),
.map-panel__cesium :deep(canvas) {
  width: 100%;
  height: 100%;
}

.map-panel__notice,
.map-panel__empty,
.map-panel__legend,
.map-panel__tools,
.map-panel__filters,
.map-panel__scale {
  position: absolute;
  z-index: 2;
}

.map-panel__filters {
  top: 16px;
  left: 50%;
  width: calc(100% - 24px);
  max-width: 920px;
  transform: translateX(-50%);
}

.map-panel__notice {
  top: 92px;
  left: 16px;
  max-width: 560px;
  border: 1px solid var(--rf-border-soft);
  border-radius: var(--rf-radius);
  background: rgba(255, 255, 255, 0.93);
  box-shadow: var(--rf-shadow-soft);
  color: #22513a;
  font-size: 13px;
  padding: 8px 12px;
}

.map-panel__notice--error {
  border-color: #fecaca;
  background: rgba(255, 245, 245, 0.94);
  color: #b91c1c;
}

.map-panel__empty {
  top: 50%;
  left: 50%;
  border-radius: var(--rf-radius);
  background: rgba(255, 255, 255, 0.92);
  color: var(--rf-text-muted);
  padding: 12px 16px;
  transform: translate(-50%, -50%);
}

.map-panel__legend {
  bottom: 16px;
  left: 16px;
  border-radius: 8px;
  background: rgba(10, 28, 22, 0.84);
  color: #fff;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.24);
  padding: 12px;
}

.map-panel__tools {
  display: grid;
  gap: 8px;
}

.map-panel__tools--left {
  top: 104px;
  left: 16px;
}

.map-panel__tools--right {
  top: 104px;
  right: 16px;
}

.map-panel__tools button {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border: 1px solid rgba(230, 238, 234, 0.88);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 8px 18px rgba(7, 36, 26, 0.18);
  color: var(--rf-text);
  cursor: pointer;
  font-size: 17px;
  transition: color 0.15s ease, background 0.15s ease, transform 0.15s ease;
}

.map-panel__tools button:hover {
  background: #fff;
  color: var(--rf-primary);
  transform: translateY(-1px);
}

.map-panel__scale {
  right: 26px;
  bottom: 22px;
  min-width: 120px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.9);
  color: #fff;
  font-size: 12px;
  font-weight: 800;
  line-height: 1.3;
  text-align: center;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.45);
}

.map-panel__scale::before,
.map-panel__scale::after {
  position: absolute;
  bottom: -2px;
  width: 2px;
  height: 10px;
  background: rgba(255, 255, 255, 0.9);
  content: "";
}

.map-panel__scale::before {
  left: 0;
}

.map-panel__scale::after {
  right: 0;
}

:deep(.cesium-viewer-bottom),
:deep(.cesium-viewer-toolbar) {
  display: none;
}

@media (max-width: 720px) {
  .map-panel__filters {
    top: 12px;
    width: calc(100% - 28px);
  }

  .map-panel__tools {
    gap: 6px;
  }

  .map-panel__tools--left,
  .map-panel__tools--right {
    top: 196px;
  }

  .map-panel__tools--left {
    left: 12px;
  }

  .map-panel__tools--right {
    right: 12px;
  }

  .map-panel__tools button {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    font-size: 16px;
  }

  .map-panel__legend {
    right: 12px;
    bottom: 12px;
    left: 12px;
    padding: 10px;
  }

  .map-panel__scale {
    right: 18px;
    bottom: 18px;
  }
}
</style>
