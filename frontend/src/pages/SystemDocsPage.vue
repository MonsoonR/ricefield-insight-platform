<template>
  <PageContainer
    title="系统说明"
    description="了解平台定位、数据来源、功能边界与未来规划。"
  >
    <ErrorState v-if="error" :message="error" compact />

    <div class="docs-top-grid">
      <section class="panel platform-card">
        <div class="platform-card__scene" aria-hidden="true">
          <span v-for="item in 6" :key="item" />
        </div>
        <div class="platform-card__content">
          <h2>稻田智研平台</h2>
          <strong>稻田数字孪生演示平台</strong>
          <p>
            本平台面向科研展示、项目汇报与教学演示，围绕稻田数字孪生场景，
            整合地块空间可视化、指标分析与预警诊断能力，辅助科研和管理决策。
          </p>
        </div>
      </section>

      <section class="panel data-card">
        <header class="section-heading">
          <div>
            <h2 class="section-title">当前数据说明</h2>
            <p class="section-subtitle">当前页面按后端标准化 API 汇总演示场景数据。</p>
          </div>
          <Badge variant="outline" class="data-mode-tag">{{ currentData.dataMode }}</Badge>
        </header>
        <dl class="data-facts">
          <div v-for="item in dataFacts" :key="item.label">
            <dt>
              <component :is="item.icon" />
              {{ item.label }}
            </dt>
            <dd>{{ item.value }}</dd>
          </div>
        </dl>
        <p class="data-note">当前数据由程序生成，不是真实采集数据，不包含真实客户数据或可识别来源材料。</p>
      </section>
    </div>

    <section class="position-grid">
      <article v-for="item in platformPositions" :key="item.title" class="panel info-card">
        <span class="info-card__icon" :class="`info-card__icon--${item.tone}`">
          <component :is="item.icon" />
        </span>
        <div>
          <h3>{{ item.title }}</h3>
          <p>{{ item.description }}</p>
        </div>
      </article>
    </section>

    <section class="panel flow-panel">
      <header class="section-heading">
        <div>
          <h2 class="section-title">数字孪生构建流程</h2>
          <p class="section-subtitle">本项目的数字孪生由地块对象、空间边界、指标时序和预警分析共同构成。</p>
        </div>
      </header>
      <div class="flow-steps">
        <article v-for="(step, index) in flowSteps" :key="step.title" class="flow-step">
          <span class="flow-step__number">{{ index + 1 }}</span>
          <span class="flow-step__icon"><component :is="step.icon" /></span>
          <h3>{{ step.title }}</h3>
          <p>{{ step.description }}</p>
        </article>
      </div>
    </section>

    <div class="docs-section-grid">
      <section class="panel list-panel">
        <h2 class="section-title">当前系统功能</h2>
        <ul class="feature-list">
          <li v-for="item in systemFeatures" :key="item.title">
            <span class="list-icon list-icon--green"><component :is="item.icon" /></span>
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.description }}</p>
            </div>
          </li>
        </ul>
      </section>

      <section class="panel list-panel">
        <h2 class="section-title">数据来源与生成方式</h2>
        <ul class="feature-list">
          <li v-for="item in dataSources" :key="item.title">
            <span class="list-icon list-icon--blue"><component :is="item.icon" /></span>
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.description }}</p>
            </div>
          </li>
        </ul>
        <p class="panel-note">当前阶段前端只消费标准化 API，不解析原始文件。</p>
      </section>

      <section class="panel list-panel boundary-panel">
        <h2 class="section-title">当前系统边界</h2>
        <ul class="boundary-list">
          <li v-for="item in systemBoundaries" :key="item">
            <CloseCircleOutlined />
            <span>{{ item }}</span>
          </li>
        </ul>
      </section>

      <section class="panel list-panel evolution-panel">
        <h2 class="section-title">未来演进方向</h2>
        <ul class="evolution-list">
          <li v-for="item in evolutionItems" :key="item">
            <CheckCircleOutlined />
            <span>{{ item }}</span>
          </li>
        </ul>
      </section>
    </div>

    <section class="panel docs-index-panel">
      <header class="section-heading">
        <div>
          <h2 class="section-title">文档索引</h2>
          <p class="section-subtitle">这些入口用于定位仓库内开发文档；当前前端不伪装成本地 Markdown 在线阅读。</p>
        </div>
      </header>
      <div class="doc-grid">
        <article v-for="doc in docs" :key="doc.key" class="doc-card">
          <span class="doc-card__icon" :class="`doc-card__icon--${doc.tone}`">
            <component :is="doc.icon" />
          </span>
          <div class="doc-card__body">
            <h3>{{ doc.key }}</h3>
            <strong>{{ doc.title }}</strong>
            <p>{{ doc.description }}</p>
            <Button variant="link" class="doc-card__action" @click="showDoc(doc)">
              查看文档入口
              <ArrowRightOutlined />
            </Button>
          </div>
        </article>
      </div>
    </section>

    <footer class="docs-footer">
      <span>稻田智研平台 © 2025</span>
      <span>版本 {{ appVersion }}</span>
      <span>用于科研展示与教学演示</span>
    </footer>

    <Sheet v-model:open="docDrawerOpen">
      <SheetContent side="right" class="w-full overflow-y-auto sm:max-w-[520px]">
        <SheetHeader>
          <SheetTitle>文档入口</SheetTitle>
          <SheetDescription>查看仓库内文档路径和用途说明。</SheetDescription>
        </SheetHeader>
        <template v-if="selectedDoc">
          <dl class="doc-detail">
            <div>
              <dt>文档名称</dt>
              <dd>{{ selectedDoc.key }}：{{ selectedDoc.title }}</dd>
            </div>
            <div>
              <dt>仓库路径</dt>
              <dd><code>{{ selectedDoc.path }}</code></dd>
            </div>
            <div>
              <dt>用途</dt>
              <dd>{{ selectedDoc.description }}</dd>
            </div>
          </dl>
          <div class="placeholder-banner">
            当前系统仅提供文档索引和仓库路径提示；如需在线阅读，需要后续配置静态文档发布或后端文档读取接口。
          </div>
        </template>
      </SheetContent>
    </Sheet>
  </PageContainer>
</template>

<script setup lang="ts">
import {
  ArrowRight as ArrowRightOutlined,
  Blocks as AppstoreOutlined,
  BookOpen as BookOutlined,
  BookOpenText as ReadOutlined,
  CalendarDays as CalendarOutlined,
  ChartColumn as BarChartOutlined,
  ChartLine as LineChartOutlined,
  CircleCheck as CheckCircleOutlined,
  CircleX as CloseCircleOutlined,
  Code as CodeOutlined,
  Compass as CompassOutlined,
  Database as DatabaseOutlined,
  FileText as FileTextOutlined,
  Flag as FlagOutlined,
  FlaskConical as ExperimentOutlined,
  MapPin as EnvironmentOutlined,
  Network as ApiOutlined,
  Presentation as FundProjectionScreenOutlined,
  Projector as ProjectOutlined,
  Rocket as DeploymentUnitOutlined,
  Route as GatewayOutlined,
  Settings as SettingOutlined,
  ShieldCheck as SafetyCertificateOutlined,
  SlidersHorizontal as SlidersOutlined,
  Sprout as GoldOutlined,
  TriangleAlert as AlertOutlined,
  Waypoints as NodeIndexOutlined,
  Wrench as ToolOutlined,
} from 'lucide-vue-next';
import type { Component } from 'vue';
import { computed, onMounted, ref } from 'vue';

import {
  fetchCurrentScenario,
  fetchDates,
  fetchMetrics,
  fetchPlots,
  fetchScenarioOverview,
  fetchWarnings,
} from '@/api';
import { ErrorState, PageContainer } from '@/components/base';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { getOverviewApiErrorMessage } from '@/services/overview';

interface DataSummary {
  dataMode: string;
  scenarioId: string;
  plotCount: number | string;
  metricCount: number | string;
  dateRange: string;
  warningCount: number | string;
}

interface IconItem {
  title: string;
  description: string;
  icon: Component;
  tone?: 'green' | 'blue' | 'purple' | 'orange' | 'red' | 'cyan';
}

interface DocItem {
  key: string;
  title: string;
  path: string;
  description: string;
  icon: Component;
  tone: 'green' | 'blue' | 'purple' | 'orange' | 'red' | 'cyan';
}

const appVersion = '0.1.0';
const fallbackScenarioId = 'demo-ricefield-2025';
const loading = ref(false);
const error = ref('');
const docDrawerOpen = ref(false);
const selectedDoc = ref<DocItem>();

const currentData = ref<DataSummary>({
  dataMode: '模拟数据',
  scenarioId: fallbackScenarioId,
  plotCount: 8,
  metricCount: 11,
  dateRange: '2025-04-03 ~ 2025-05-17',
  warningCount: '读取中',
});

const dataFacts = computed(() => [
  { label: '场景 ID', value: currentData.value.scenarioId, icon: DatabaseOutlined },
  { label: '地块数量', value: formatCount(currentData.value.plotCount, '个'), icon: EnvironmentOutlined },
  { label: '指标数量', value: formatCount(currentData.value.metricCount, '个'), icon: ExperimentOutlined },
  { label: '时间范围', value: currentData.value.dateRange, icon: CalendarOutlined },
  { label: '预警数量', value: formatCount(currentData.value.warningCount, '条'), icon: AlertOutlined },
]);

const platformPositions: IconItem[] = [
  {
    title: '科研展示',
    description: '可视化呈现稻田生长、土壤与环境指标变化。',
    icon: FundProjectionScreenOutlined,
    tone: 'green',
  },
  {
    title: '项目汇报',
    description: '支撑项目汇报、成果展示与能力演示。',
    icon: ProjectOutlined,
    tone: 'blue',
  },
  {
    title: '教学演示',
    description: '服务教学场景，帮助理解数字孪生理念。',
    icon: ReadOutlined,
    tone: 'cyan',
  },
];

const flowSteps: IconItem[] = [
  { title: '稻田地块实体', description: '以可识别的地块作为管理单元。', icon: GoldOutlined },
  { title: '程序生成边界', description: '生成示例地块空间边界与区域划分。', icon: NodeIndexOutlined },
  { title: '构建数字对象', description: '形成场景、地块、边界和时间对象。', icon: AppstoreOutlined },
  { title: '绑定多源指标', description: '用指标字典组织作物、土壤和环境时序。', icon: BarChartOutlined },
  { title: '可视化与分析', description: '通过地图、图表和表格解释状态变化。', icon: LineChartOutlined },
  { title: '预警与辅助决策', description: '识别异常风险，提供谨慎的核验参考。', icon: SafetyCertificateOutlined },
];

const systemFeatures: IconItem[] = [
  { title: '场景驾驶舱', description: '汇总场景概况、关键指标、区域状态与重点关注地块。', icon: CompassOutlined },
  { title: 'Cesium 地图孪生', description: '展示地块空间边界、指标着色、点击详情和图层联动。', icon: EnvironmentOutlined },
  { title: '地块画像', description: '查看单个地块的基础信息、指标快照、趋势和预警建议。', icon: GatewayOutlined },
  { title: '指标对比', description: '对比不同地块的指标差异、区域均值和状态分布。', icon: BarChartOutlined },
  { title: '预警分析', description: '汇总质量异常与农情风险，定位受影响地块和指标。', icon: AlertOutlined },
  { title: '系统说明', description: '说明平台定位、数据来源、功能边界、演进方向和文档索引。', icon: BookOutlined },
];

const dataSources: IconItem[] = [
  { title: '模拟数据生成', description: '由后端程序生成演示用地块、指标和时序观测。', icon: DatabaseOutlined },
  { title: '程序生成地块边界', description: '用程序生成 8 个示例地块边界，用于空间可视化验证。', icon: NodeIndexOutlined },
  { title: '指标字典定义', description: '11 个指标先进入指标字典，再进入页面分析。', icon: SlidersOutlined },
  { title: '质量与预警注入', description: '模拟缺失、异常和错误状态，验证质量展示与预警链路。', icon: AlertOutlined },
  { title: '未来可接入真实数据', description: '在合规数据治理、标准化 API 和正式数据层准备完成后接入。', icon: DeploymentUnitOutlined },
];

const systemBoundaries = [
  '不做 Excel 导入',
  '不做 GeoJSON、PDF、图片等文件导入',
  '不做数据导入中心与导入报告',
  '不保存真实客户数据或可识别来源数据',
  '不做复杂三维资产与高级空间分析',
  '不做 AI 决策自动化处方推荐',
];

const evolutionItems = [
  '接入 PostgreSQL + PostGIS 正式数据层',
  '对接数据采集设备或传感器',
  '扩展更多作物与更多指标',
  '完善预警规则与风险评估模型',
  '增强可视化分析与报表能力',
  '支持多项目、多角色与权限管理',
  '部署到生产环境 Docker + Nginx',
];

const docs: DocItem[] = [
  { key: 'PROJECT_PLAN', title: '项目计划', path: 'docs/PROJECT_PLAN.md', description: '项目定位、阶段范围、技术路线和成功标准。', icon: ProjectOutlined, tone: 'green' },
  { key: 'ARCHITECTURE', title: '系统架构', path: 'docs/ARCHITECTURE.md', description: '前后端架构、数据流和模块职责。', icon: DeploymentUnitOutlined, tone: 'blue' },
  { key: 'DATA_MODEL', title: '数据模型', path: 'docs/DATA_MODEL.md', description: '核心数据实体、字段与关系。', icon: DatabaseOutlined, tone: 'green' },
  { key: 'API', title: 'API 文档', path: 'docs/API.md', description: '接口说明、请求参数与响应结构。', icon: ApiOutlined, tone: 'purple' },
  { key: 'DESIGN_SYSTEM', title: '设计系统', path: 'docs/DESIGN_SYSTEM.md', description: '视觉规范、组件规范和页面布局约束。', icon: SlidersOutlined, tone: 'orange' },
  { key: 'FRONTEND_GUIDE', title: '前端指南', path: 'docs/FRONTEND_GUIDE.md', description: '前端架构、组件分工和页面开发规则。', icon: CodeOutlined, tone: 'cyan' },
  { key: 'BACKEND_GUIDE', title: '后端指南', path: 'docs/BACKEND_GUIDE.md', description: '后端结构、服务层约定和测试方式。', icon: ToolOutlined, tone: 'blue' },
  { key: 'USER_MANUAL', title: '用户手册', path: 'docs/USER_MANUAL.md', description: '各页面功能与用户操作说明。', icon: ReadOutlined, tone: 'green' },
  { key: 'DEPLOYMENT', title: '部署说明', path: 'docs/DEPLOYMENT.md', description: '环境要求、部署步骤与运维说明。', icon: DeploymentUnitOutlined, tone: 'red' },
  { key: 'IMPORT_GUIDE', title: '模拟数据指南', path: 'docs/IMPORT_GUIDE.md', description: '模拟场景、地块边界和观测数据生成说明。', icon: FileTextOutlined, tone: 'purple' },
  { key: 'METRIC_DICTIONARY', title: '指标字典', path: 'docs/METRIC_DICTIONARY.md', description: '指标定义、单位、范围和使用口径。', icon: SettingOutlined, tone: 'green' },
  { key: 'CHANGELOG', title: '变更记录', path: 'docs/CHANGELOG.md', description: '版本更新、文档同步和验证记录。', icon: FlagOutlined, tone: 'cyan' },
];

onMounted(loadSystemData);

async function loadSystemData() {
  loading.value = true;
  error.value = '';

  try {
    const overview = await fetchScenarioOverview(fallbackScenarioId);
    const [scenarioResult, metricsResult, plotsResult, datesResult, warningsResult] = await Promise.allSettled([
      fetchCurrentScenario(),
      fetchMetrics(),
      fetchPlots(),
      fetchDates(),
      fetchWarnings(),
    ]);

    const scenario = scenarioResult.status === 'fulfilled' ? scenarioResult.value : overview.scenario;
    const metricTotal = metricsResult.status === 'fulfilled' ? metricsResult.value.total : scenario.metric_count;
    const plotTotal = plotsResult.status === 'fulfilled' ? plotsResult.value.total : scenario.plot_count;
    const dates = datesResult.status === 'fulfilled' ? datesResult.value.items : [];
    const warningTotal = warningsResult.status === 'fulfilled' ? warningsResult.value.total : findStatValue(overview, '预警数量');
    const startDate = dates.length ? dates[0] : scenario.date_range.start_date;
    const endDate = dates.length ? dates[dates.length - 1] : scenario.date_range.end_date;

    currentData.value = {
      dataMode: formatDataMode(scenario.data_mode),
      scenarioId: scenario.scenario_id,
      plotCount: plotTotal,
      metricCount: metricTotal,
      dateRange: startDate && endDate ? `${startDate} ~ ${endDate}` : '暂无观测日期',
      warningCount: warningTotal,
    };
  } catch (loadError) {
    error.value = getOverviewApiErrorMessage(loadError, '系统说明页数据读取失败，已显示默认演示信息。');
  } finally {
    loading.value = false;
  }
}

function formatDataMode(mode: string) {
  if (mode === 'demo' || mode === 'mock' || mode === 'simulated') {
    return '模拟数据';
  }
  return mode || '模拟数据';
}

function findStatValue(overview: Awaited<ReturnType<typeof fetchScenarioOverview>>, label: string) {
  return overview.stat_cards.find((item) => item.label === label)?.value ?? '暂无';
}

function formatCount(value: number | string, unit: string) {
  if (typeof value === 'number') {
    return `${value} ${unit}`;
  }
  if (/^\d+$/.test(value)) {
    return `${value} ${unit}`;
  }
  return value;
}

function showDoc(doc: DocItem) {
  selectedDoc.value = doc;
  docDrawerOpen.value = true;
}
</script>

<style scoped>
.docs-top-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 390px;
  gap: 16px;
}

.platform-card {
  position: relative;
  display: grid;
  min-height: 250px;
  overflow: hidden;
  padding: 32px 36px;
  background:
    linear-gradient(105deg, color-mix(in srgb, var(--rf-primary-soft) 92%, white), color-mix(in srgb, var(--rf-surface) 86%, transparent)),
    repeating-linear-gradient(135deg, color-mix(in srgb, var(--rf-primary-line) 25%, transparent) 0 1px, transparent 1px 34px);
}

.platform-card__scene {
  position: absolute;
  left: 28px;
  bottom: 24px;
  display: flex;
  align-items: flex-end;
  gap: 7px;
  width: 180px;
  height: 86px;
  opacity: 0.35;
}

.platform-card__scene span {
  flex: 1;
  border-radius: 999px 999px 0 0;
  background: linear-gradient(180deg, var(--rf-primary-line), var(--rf-primary));
}

.platform-card__scene span:nth-child(2n) {
  height: 62%;
}

.platform-card__scene span:nth-child(2n + 1) {
  height: 88%;
}

.platform-card__content {
  position: relative;
  z-index: 1;
  max-width: 760px;
  padding-left: 200px;
}

.platform-card h2 {
  margin: 0 0 10px;
  color: var(--rf-text);
  font-size: 30px;
  font-weight: 800;
  line-height: 1.2;
}

.platform-card strong {
  display: block;
  color: var(--rf-primary);
  font-size: 20px;
  line-height: 1.35;
}

.platform-card p {
  margin: 26px 0 0;
  color: var(--rf-text-muted);
  font-size: 14px;
  line-height: 1.85;
}

.data-card,
.flow-panel,
.list-panel,
.docs-index-panel {
  padding: 20px;
}

.section-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.data-mode-tag {
  margin: 0;
  color: var(--rf-primary);
  background: var(--rf-primary-soft);
  font-weight: 700;
}

.data-facts {
  display: grid;
  gap: 10px;
  margin: 18px 0 0;
}

.data-facts div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid var(--rf-border-soft);
  padding-bottom: 9px;
}

.data-facts dt {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--rf-text-muted);
  font-size: 13px;
  font-weight: 600;
}

.data-facts dd {
  margin: 0;
  color: var(--rf-text);
  font-size: 13px;
  font-weight: 800;
  text-align: right;
}

.data-note,
.panel-note {
  margin: 16px 0 0;
  border-radius: var(--rf-radius);
  background: var(--rf-surface-soft);
  color: var(--rf-text-muted);
  padding: 10px 12px;
  font-size: 13px;
  line-height: 1.6;
}

.position-grid,
.docs-section-grid,
.doc-grid {
  display: grid;
  gap: 16px;
}

.position-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.info-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 18px 20px;
}

.info-card__icon,
.list-icon,
.doc-card__icon,
.flow-step__icon {
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 50%;
}

.info-card__icon {
  width: 42px;
  height: 42px;
  color: var(--tone);
  background: color-mix(in srgb, var(--tone) 12%, white);
  font-size: 18px;
}

.info-card__icon--green,
.doc-card__icon--green {
  --tone: var(--rf-primary);
}

.info-card__icon--blue,
.doc-card__icon--blue {
  --tone: var(--rf-info);
}

.info-card__icon--cyan,
.doc-card__icon--cyan {
  --tone: var(--rf-accent-cyan);
}

.doc-card__icon--purple {
  --tone: var(--rf-purple);
}

.doc-card__icon--orange {
  --tone: var(--rf-status-warning);
}

.doc-card__icon--red {
  --tone: var(--rf-status-critical);
}

.info-card h3,
.flow-step h3,
.doc-card h3 {
  margin: 0;
  color: var(--rf-text);
  font-size: 15px;
  font-weight: 800;
  line-height: 1.35;
}

.info-card p,
.flow-step p,
.doc-card p,
.feature-list p {
  margin: 6px 0 0;
  color: var(--rf-text-muted);
  font-size: 13px;
  line-height: 1.65;
}

.flow-steps {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 14px;
  margin-top: 18px;
}

.flow-step {
  position: relative;
  min-height: 164px;
  border: 1px solid var(--rf-border);
  border-radius: 10px;
  background: var(--rf-surface);
  padding: 18px 14px 16px;
}

.flow-step::after {
  content: "";
  position: absolute;
  top: 78px;
  right: -12px;
  width: 22px;
  height: 1px;
  background: var(--rf-primary);
}

.flow-step:last-child::after {
  content: none;
}

.flow-step__number {
  position: absolute;
  top: 12px;
  right: 12px;
  color: var(--rf-text-soft);
  font-size: 12px;
  font-weight: 800;
}

.flow-step__icon {
  width: 42px;
  height: 42px;
  margin-bottom: 14px;
  color: var(--rf-primary);
  background: var(--rf-primary-soft);
  font-size: 19px;
}

.docs-section-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.feature-list,
.boundary-list,
.evolution-list {
  display: grid;
  gap: 12px;
  margin: 16px 0 0;
  padding: 0;
  list-style: none;
}

.feature-list li {
  display: flex;
  gap: 10px;
}

.feature-list strong {
  display: block;
  color: var(--rf-text);
  font-size: 13px;
  line-height: 1.4;
}

.list-icon {
  width: 30px;
  height: 30px;
  margin-top: 1px;
  font-size: 14px;
}

.list-icon--green {
  color: var(--rf-primary);
  background: var(--rf-primary-soft);
}

.list-icon--blue {
  color: var(--rf-info);
  background: color-mix(in srgb, var(--rf-info) 10%, white);
}

.boundary-panel {
  background: linear-gradient(135deg, var(--rf-status-critical-bg), var(--rf-surface) 48%);
}

.boundary-list li,
.evolution-list li {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  color: var(--rf-text);
  font-size: 13px;
  line-height: 1.6;
}

.boundary-list svg {
  flex: 0 0 auto;
  margin-top: 3px;
  color: var(--rf-status-critical);
}

.evolution-list svg {
  flex: 0 0 auto;
  margin-top: 3px;
  color: var(--rf-status-normal);
}

.evolution-panel {
  background: linear-gradient(135deg, var(--rf-status-normal-bg), var(--rf-surface) 48%);
}

.doc-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-top: 18px;
}

.doc-card {
  display: grid;
  grid-template-columns: 46px minmax(0, 1fr);
  gap: 12px;
  min-height: 134px;
  border: 1px solid var(--rf-border);
  border-radius: 10px;
  background: var(--rf-surface);
  padding: 14px;
}

.doc-card__icon {
  width: 42px;
  height: 42px;
  color: var(--tone);
  background: color-mix(in srgb, var(--tone) 12%, white);
  font-size: 18px;
}

.doc-card__body {
  min-width: 0;
}

.doc-card h3 {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
}

.doc-card strong {
  display: block;
  margin-top: 4px;
  color: var(--rf-text);
  font-size: 13px;
}

.doc-card__action {
  height: auto;
  margin-top: 8px;
  padding: 0;
  color: var(--rf-primary);
  font-size: 13px;
  font-weight: 800;
}

.docs-footer {
  display: flex;
  justify-content: center;
  gap: 18px;
  color: var(--rf-text-soft);
  font-size: 12px;
}

.doc-detail {
  display: grid;
  gap: 14px;
  margin: 0 0 18px;
}

.doc-detail div {
  border: 1px solid var(--rf-border-soft);
  border-radius: var(--rf-radius);
  background: var(--rf-surface-soft);
  padding: 12px;
}

.doc-detail dt {
  color: var(--rf-text-muted);
  font-size: 12px;
}

.doc-detail dd {
  margin: 6px 0 0;
  color: var(--rf-text);
  font-weight: 800;
  line-height: 1.5;
  word-break: break-all;
}

@media (max-width: 1320px) {
  .docs-section-grid {
    grid-template-columns: 1fr 1fr;
  }

  .doc-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 1180px) {
  .docs-top-grid,
  .flow-steps {
    grid-template-columns: 1fr 1fr;
  }

  .flow-step::after {
    content: none;
  }
}

@media (max-width: 980px) {
  .docs-top-grid,
  .position-grid,
  .docs-section-grid,
  .flow-steps,
  .doc-grid {
    grid-template-columns: 1fr;
  }

  .platform-card__content {
    padding-left: 0;
  }

  .platform-card__scene {
    display: none;
  }

  .flow-step::after {
    content: none;
  }
}

@media (max-width: 640px) {
  .platform-card {
    padding: 24px;
  }

  .platform-card h2 {
    font-size: 24px;
  }

  .platform-card strong {
    font-size: 18px;
  }

  .section-heading,
  .data-facts div,
  .docs-footer {
    display: block;
  }

  .data-facts dd {
    margin-top: 4px;
    text-align: left;
  }

  .docs-footer span {
    display: block;
    text-align: center;
  }
}
</style>
