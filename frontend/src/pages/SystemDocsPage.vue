<template>
  <PageContainer
    title="系统说明"
    description="了解平台定位、数据来源、功能边界与后续演进方向。"
  >
    <div class="docs-hero">
      <section class="panel docs-position">
        <div>
          <h2>稻田智研平台</h2>
          <strong>稻田数字孪生演示平台</strong>
          <p>面向科研展示、项目汇报和教学演示，使用后端程序生成的模拟稻田场景，展示地块空间可视化、指标分析和预警识别能力。</p>
        </div>
      </section>
      <section class="panel docs-data">
        <h2>当前数据说明</h2>
        <a-tag color="success">模拟数据</a-tag>
        <ul>
          <li>场景 ID：demo-ricefield-2025</li>
          <li>地块数量：8 个</li>
          <li>指标数量：11 个</li>
          <li>观测周期：2025-04-03 至 2025-05-17</li>
          <li>预警数量：12 条</li>
        </ul>
      </section>
    </div>

    <section class="panel docs-flow">
      <h2 class="section-title">数字孪生构建流程</h2>
      <div class="docs-flow__steps">
        <div v-for="step in flowSteps" :key="step.title">
          <strong>{{ step.title }}</strong>
          <span>{{ step.description }}</span>
        </div>
      </div>
    </section>

    <div class="page-grid page-grid--four">
      <section class="panel docs-recommend">
        <h2 class="section-title">当前系统功能</h2>
        <ul>
          <li>场景驾驶舱：汇总场景、健康度和关键指标。</li>
          <li>Cesium 地图孪生：地块边界、指标着色和点击联动。</li>
          <li>地块画像：单地块指标快照、趋势和来源追溯。</li>
          <li>指标对比：多地块指标排行与状态分布。</li>
          <li>预警分析：缺失、异常和错误预警识别。</li>
        </ul>
      </section>
      <section class="panel docs-recommend docs-boundary">
        <h2 class="section-title">当前系统边界</h2>
        <ul>
          <li>不做 Excel、GeoJSON、PDF、图片等文件导入。</li>
          <li>不提供原始文件处理主线与文件处理报告。</li>
          <li>不保存真实客户数据或可识别来源数据。</li>
          <li>不提供文件上传、自动报告和权限系统。</li>
          <li>不实现复杂三维资产与复杂空间分析。</li>
        </ul>
      </section>
      <section class="panel docs-recommend">
        <h2 class="section-title">后续演进方向</h2>
        <ul>
          <li>接入 PostgreSQL + PostGIS 正式数据层。</li>
          <li>对接合规遥感、传感器或人工观测数据。</li>
          <li>扩展更多作物生长、土壤和环境指标。</li>
          <li>完善预警规则与风险评估模型。</li>
          <li>部署到生产环境 Docker + Nginx。</li>
        </ul>
      </section>
      <section class="panel docs-recommend">
        <h2 class="section-title">文档搜索</h2>
        <a-input v-model:value="keyword" allow-clear placeholder="搜索文档名称、关键词或路径..." />
        <div class="docs-tabs">
          <button
            v-for="category in categories"
            :key="category"
            :class="{ active: selectedCategory === category }"
            type="button"
            @click="selectCategory(category)"
          >
            {{ category }}
          </button>
        </div>
      </section>
    </div>

    <DataTable
      title="文档目录"
      :columns="columns"
      :data-source="filteredDocs"
      row-key="path"
      :pagination="{ pageSize: 12 }"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag color="success">{{ record.status }}</a-tag>
        </template>
        <template v-if="column.key === 'action'">
          <a-button type="link" @click="showDoc(record as DocRow)">查看说明</a-button>
        </template>
      </template>
    </DataTable>

    <a-drawer
      v-model:open="docDrawerOpen"
      title="文档说明"
      width="520"
      :destroy-on-close="true"
    >
      <template v-if="selectedDoc">
        <dl class="doc-detail">
          <div>
            <dt>文档名称</dt>
            <dd>{{ selectedDoc.name }}</dd>
          </div>
          <div>
            <dt>分类</dt>
            <dd>{{ selectedDoc.category }}</dd>
          </div>
          <div>
            <dt>仓库路径</dt>
            <dd><code>{{ selectedDoc.path }}</code></dd>
          </div>
          <div>
            <dt>用途</dt>
            <dd>{{ selectedDoc.purpose }}</dd>
          </div>
          <div>
            <dt>维护状态</dt>
            <dd>{{ selectedDoc.status }}</dd>
          </div>
        </dl>
        <div class="placeholder-banner">
          当前前端先提供文档索引和维护说明；Markdown 在线阅读需要后续增加后端文档读取接口或静态文档发布目录。
        </div>
      </template>
    </a-drawer>
  </PageContainer>
</template>

<script setup lang="ts">
import type { TableColumnsType } from 'ant-design-vue';
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import { DataTable, PageContainer } from '@/components/base';

interface DocRow {
  name: string;
  category: string;
  path: string;
  purpose: string;
  status: string;
}

const keyword = ref('');
const selectedCategory = ref('全部');
const selectedDoc = ref<DocRow>();
const docDrawerOpen = ref(false);
const route = useRoute();

const docs: DocRow[] = [
  { name: 'PROJECT_PLAN.md', category: '项目总览', path: 'docs/PROJECT_PLAN.md', purpose: '项目目标、范围、里程碑与阶段性计划', status: '已维护' },
  { name: 'ARCHITECTURE.md', category: '架构设计', path: 'docs/ARCHITECTURE.md', purpose: '系统架构设计与技术选型说明', status: '已维护' },
  { name: 'DATA_MODEL.md', category: '数据模型', path: 'docs/DATA_MODEL.md', purpose: '核心数据模型与表结构设计', status: '已维护' },
  { name: 'METRIC_DICTIONARY.md', category: '指标字典', path: 'docs/METRIC_DICTIONARY.md', purpose: '指标定义、计算逻辑与口径说明', status: '已维护' },
  { name: 'API.md', category: 'API 接口', path: 'docs/API.md', purpose: '后端接口文档与参数说明', status: '已维护' },
  { name: 'DESIGN_SYSTEM.md', category: '前端开发', path: 'docs/DESIGN_SYSTEM.md', purpose: '设计系统规范、组件与视觉语言', status: '已维护' },
  { name: 'FRONTEND_GUIDE.md', category: '前端开发', path: 'docs/FRONTEND_GUIDE.md', purpose: '前端开发环境、目录结构与开发指南', status: '已维护' },
  { name: 'BACKEND_GUIDE.md', category: '后端开发', path: 'docs/BACKEND_GUIDE.md', purpose: '后端服务结构、开发规范与本地启动', status: '已维护' },
  { name: 'IMPORT_GUIDE.md', category: '模拟场景', path: 'docs/IMPORT_GUIDE.md', purpose: '模拟场景生成、地块边界和观测数据说明', status: '已维护' },
  { name: 'USER_MANUAL.md', category: '用户手册', path: 'docs/USER_MANUAL.md', purpose: '平台功能使用说明与操作指引', status: '已维护' },
  { name: 'DEPLOYMENT.md', category: '部署交付', path: 'docs/DEPLOYMENT.md', purpose: '环境部署、配置与运维流程', status: '已维护' },
  { name: 'CODEX_WORKFLOW.md', category: 'Codex 协作', path: 'docs/CODEX_WORKFLOW.md', purpose: '给 Codex 的开发流程与协作规范', status: '已维护' },
];

const categories = computed(() => ['全部', ...new Set(docs.map((item) => item.category))]);
const filteredDocs = computed(() =>
  docs.filter((doc) => {
    const categoryMatch = selectedCategory.value === '全部' || doc.category === selectedCategory.value;
    const search = `${doc.name} ${doc.path} ${doc.purpose}`.toLowerCase();
    return categoryMatch && (!keyword.value || search.includes(keyword.value.toLowerCase()));
  }),
);
const flowSteps = [
  { title: '1. 稻田地块实体', description: '生成可演示的稻田地块与管理单元。' },
  { title: '2. 程序生成边界', description: '使用程序生成示例地块空间边界。' },
  { title: '3. 构建孪生对象', description: '绑定场景、地块、指标和观测时间。' },
  { title: '4. 绑定多源指标', description: '用指标字典组织作物、土壤和环境指标。' },
  { title: '5. 可视化与分析', description: '地图、图表和表格形成分析闭环。' },
  { title: '6. 预警与辅助决策', description: '识别状态异常并给出巡田参考。' },
];

const columns: TableColumnsType = [
  { title: '文档名称', dataIndex: 'name', key: 'name' },
  { title: '分类', dataIndex: 'category', key: 'category' },
  { title: '路径', dataIndex: 'path', key: 'path' },
  { title: '用途', dataIndex: 'purpose', key: 'purpose' },
  { title: '状态', dataIndex: 'status', key: 'status', width: 110 },
  { title: '操作', key: 'action', width: 120 },
];

function selectCategory(category: string) {
  selectedCategory.value = category;
}

function showDoc(doc: DocRow) {
  selectedDoc.value = doc;
  selectedCategory.value = doc.category;
  docDrawerOpen.value = true;
}

function openDocFromQuery() {
  const docName = typeof route.query.doc === 'string' ? route.query.doc : '';
  const doc = docs.find((item) => item.name === docName);
  if (doc) {
    showDoc(doc);
  }
}

onMounted(openDocFromQuery);
watch(() => route.query.doc, openDocFromQuery);
</script>

<style scoped>
.docs-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 380px;
  gap: 16px;
}

.docs-position,
.docs-data,
.docs-flow,
.docs-recommend {
  padding: 20px;
}

.docs-position {
  min-height: 220px;
  background:
    linear-gradient(90deg, rgba(232, 246, 239, 0.95), rgba(255, 255, 255, 0.76)),
    repeating-linear-gradient(120deg, rgba(21, 144, 93, 0.10) 0 1px, transparent 1px 34px);
}

.docs-position h2,
.docs-position strong {
  display: block;
}

.docs-position h2 {
  margin: 16px 0 8px;
  color: var(--rf-text);
  font-size: 34px;
}

.docs-position strong {
  color: var(--rf-primary);
  font-size: 22px;
}

.docs-position p {
  max-width: 720px;
  color: var(--rf-text-muted);
  font-size: 15px;
  line-height: 1.8;
}

.docs-data ul {
  margin: 16px 0 0;
  padding-left: 18px;
  color: var(--rf-text-muted);
  line-height: 1.9;
}

.docs-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.docs-tabs button,
.docs-recommend button {
  cursor: pointer;
  font-family: inherit;
}

.docs-tabs button {
  border: 0;
  border-radius: 7px;
  background: #f1f5f3;
  color: var(--rf-text-muted);
  font-weight: 800;
  padding: 9px 14px;
}

.docs-tabs button.active {
  background: var(--rf-primary);
  color: #fff;
}

.docs-flow__steps {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 14px;
  margin-top: 18px;
}

.docs-flow__steps div {
  min-height: 126px;
  border: 1px solid var(--rf-border-soft);
  border-radius: 8px;
  background: #fbfdfc;
  padding: 16px;
}

.docs-flow__steps strong,
.docs-flow__steps span {
  display: block;
}

.docs-flow__steps strong {
  color: var(--rf-text);
}

.docs-flow__steps span {
  margin-top: 10px;
  color: var(--rf-text-muted);
  font-size: 13px;
  line-height: 1.7;
}

.docs-recommend div {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.docs-recommend button {
  border: 0;
  border-radius: 999px;
  background: #eef7f1;
  color: var(--rf-primary);
  font-size: 12px;
  font-weight: 800;
  padding: 6px 10px;
}

.docs-recommend ul {
  margin: 14px 0 0;
  padding-left: 18px;
  color: var(--rf-text-muted);
  line-height: 1.8;
}

.docs-boundary {
  background: linear-gradient(135deg, #fff8f5, #ffffff);
}

.doc-detail {
  display: grid;
  gap: 14px;
  margin: 0 0 18px;
}

.doc-detail div {
  border: 1px solid var(--rf-border-soft);
  border-radius: 8px;
  background: #f8fbfa;
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
}

@media (max-width: 1280px) {
  .docs-hero,
  .docs-flow__steps {
    grid-template-columns: 1fr;
  }
}
</style>
