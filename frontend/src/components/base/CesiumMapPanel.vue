<template>
  <section class="map-panel">
    <header v-if="title || $slots.toolbar" class="map-panel__header">
      <div>
        <h2>{{ title }}</h2>
        <p>{{ featureCount }} 个地块 · 卫星底图 + 地块指标图层</p>
      </div>
      <slot name="toolbar" />
    </header>
    <div class="map-panel__canvas" :style="{ minHeight: `${height}px` }">
      <div ref="containerRef" class="map-panel__cesium" />
      <div class="map-panel__tools">
        <button type="button" @click="zoomHome">全图</button>
        <button type="button" @click="toggleAlpha">透明度</button>
      </div>
      <div v-if="imageryError" class="map-panel__notice map-panel__notice--error">
        {{ imageryError }}
      </div>
      <div v-else-if="loading" class="map-panel__notice">正在加载地图图层...</div>
      <div v-if="empty" class="map-panel__empty">暂无可展示地块</div>
      <div v-if="$slots.legend" class="map-panel__legend">
        <slot name="legend" />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import {
  Cartographic,
  Cartesian2,
  Cartesian3,
  Color,
  ColorMaterialProperty,
  ConstantProperty,
  GeoJsonDataSource,
  Ion,
  IonWorldImageryStyle,
  Math as CesiumMath,
  PolylineDashMaterialProperty,
  ScreenSpaceEventHandler,
  ScreenSpaceEventType,
  UrlTemplateImageryProvider,
  Viewer,
  createWorldImageryAsync,
  type Entity,
} from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css';
import { computed, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue';

import {
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
  }>(),
  {
    title: '地块分布图',
    height: 520,
    loading: false,
    selectedPlotId: undefined,
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
const polygonAlpha = ref(0.36);
const outlineEntities: Entity[] = [];
let clickHandler: ScreenSpaceEventHandler | undefined;
let renderRequestId = 0;

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

  await setupImageryLayer();

  clickHandler = new ScreenSpaceEventHandler(viewer.value.scene.canvas);
  clickHandler.setInputAction((movement: ScreenSpaceEventHandler.PositionedEvent) => {
    selectFeatureAtPosition(movement.position);
  }, ScreenSpaceEventType.LEFT_CLICK);

  void renderGeoJson();
});

onBeforeUnmount(() => {
  renderRequestId += 1;
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
  () => props.selectedPlotId,
  () => {
    applyEntityStyles();
    renderOutlines();
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
    applyEntityStyles();
    renderOutlines();
    await viewer.value.zoomTo(nextDataSource);
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
    const isSelected = properties.plot_id === props.selectedPlotId;
    const alpha = Math.min(Math.max(polygonAlpha.value + (isSelected ? 0.12 : 0), 0.25), 0.48);

    polygon.material = new ColorMaterialProperty(
      Color.fromCssColorString(style.fillColor).withAlpha(alpha),
    );
    polygon.outline = new ConstantProperty(false);
  });
}

function renderOutlines() {
  if (!viewer.value) {
    return;
  }

  clearOutlines();

  props.featureCollection.features.forEach((feature) => {
    const style = resolvePlotVisualStyle(feature.properties);
    const isSelected = feature.properties.plot_id === props.selectedPlotId;
    const rings = getOuterRings(feature.geometry);

    rings.forEach((ring) => {
      const positions = Cartesian3.fromDegreesArray(ring.flatMap(([lng, lat]) => [lng, lat]));
      const outline = viewer.value?.entities.add({
        properties: feature.properties,
        polyline: {
          positions,
          clampToGround: new ConstantProperty(true),
          width: style.outlineWidth + (isSelected ? 1.6 : 0),
          material: style.dashedOutline
            ? new PolylineDashMaterialProperty({
                color: Color.fromCssColorString(style.outlineColor).withAlpha(0.96),
                dashLength: 14,
              })
            : new ColorMaterialProperty(
                Color.fromCssColorString(style.outlineColor).withAlpha(isSelected ? 1 : 0.92),
              ),
        },
      });

      if (outline) {
        outlineEntities.push(outline);
      }
    });
  });
}

function clearOutlines() {
  if (!viewer.value || viewer.value.isDestroyed()) {
    outlineEntities.length = 0;
    return;
  }

  outlineEntities.splice(0).forEach((entity) => viewer.value?.entities.remove(entity));
}

function clearDataSource() {
  clearOutlines();

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
    void viewer.value?.zoomTo(dataSource.value);
  }
}

function toggleAlpha() {
  polygonAlpha.value = polygonAlpha.value > 0.4 ? 0.28 : 0.42;
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

.map-panel__cesium {
  position: absolute;
  inset: 0;
}

.map-panel__notice,
.map-panel__empty,
.map-panel__legend,
.map-panel__tools {
  position: absolute;
  z-index: 2;
}

.map-panel__notice {
  top: 14px;
  left: 14px;
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
  top: 14px;
  right: 14px;
  display: grid;
  gap: 8px;
}

.map-panel__tools button {
  min-width: 54px;
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.94);
  color: var(--rf-text);
  cursor: pointer;
  font-size: 12px;
  font-weight: 800;
  padding: 7px 10px;
}

:deep(.cesium-viewer-bottom),
:deep(.cesium-viewer-toolbar) {
  display: none;
}
</style>
