<template>
  <PageContainer
    title="系统文档"
    description="集中管理项目文档、规范与开发指引，帮助团队高效协作与知识沉淀。"
  >
    <div class="docs-hero">
      <div class="docs-search panel">
        <a-input v-model:value="keyword" size="large" allow-clear placeholder="搜索文档名称、关键词或路径..." />
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
      </div>
      <section class="panel docs-flow">
        <h2>给 Codex 的开发流程</h2>
        <p>面向 AI 开发助手的标准开发流程与协作规范，帮助理解项目结构、编码规范与提交流程。</p>
        <a-button block type="primary" @click="showDoc(codexDoc)">查看流程</a-button>
      </section>
      <section class="panel docs-common">
        <h2>常用文档</h2>
        <button v-for="item in commonDocs" :key="item.path" type="button" @click="showDoc(item)">
          <span>{{ item.name }}</span>
          <strong>›</strong>
        </button>
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

    <div class="page-grid page-grid--three">
      <section class="panel docs-recommend">
        <h2 class="section-title">推荐文档</h2>
        <button v-for="doc in recommendedDocs" :key="doc.path" type="button" @click="showDoc(doc)">
          {{ doc.name }}
        </button>
      </section>
      <section class="panel docs-recommend">
        <h2 class="section-title">维护提示</h2>
        <ul>
          <li>新增 API 后更新 API.md。</li>
          <li>新增指标后更新 METRIC_DICTIONARY.md。</li>
          <li>修改页面结构后更新 FRONTEND_GUIDE.md。</li>
          <li>修改模拟场景生成规则后更新 IMPORT_GUIDE.md。</li>
          <li>每轮任务更新 CHANGELOG.md。</li>
        </ul>
      </section>
      <section class="panel docs-recommend">
        <h2 class="section-title">当前页面结构</h2>
        <ul>
          <li>场景驾驶舱、Cesium 地图孪生、地块画像。</li>
          <li>指标对比、预警分析、系统说明。</li>
          <li>第一阶段不提供 Excel 导入中心。</li>
        </ul>
      </section>
    </div>

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

const codexDoc = computed(() => docs.find((doc) => doc.name === 'CODEX_WORKFLOW.md') ?? docs[0]);
const categories = computed(() => ['全部', ...new Set(docs.map((item) => item.category))]);
const filteredDocs = computed(() =>
  docs.filter((doc) => {
    const categoryMatch = selectedCategory.value === '全部' || doc.category === selectedCategory.value;
    const search = `${doc.name} ${doc.path} ${doc.purpose}`.toLowerCase();
    return categoryMatch && (!keyword.value || search.includes(keyword.value.toLowerCase()));
  }),
);
const commonDocs = docs.filter((doc) => ['API.md', 'DATA_MODEL.md', 'DEPLOYMENT.md', 'FRONTEND_GUIDE.md'].includes(doc.name));
const recommendedDocs = docs;

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
  grid-template-columns: minmax(0, 1fr) 360px 360px;
  gap: 14px;
}

.docs-search,
.docs-flow,
.docs-common,
.docs-recommend {
  padding: 18px;
}

.docs-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.docs-tabs button,
.docs-common button,
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

.docs-flow {
  background: linear-gradient(135deg, #f0fdf4, #ffffff);
}

.docs-flow h2,
.docs-common h2 {
  margin: 0;
  font-size: 18px;
}

.docs-flow p {
  color: var(--rf-text-muted);
  line-height: 1.7;
}

.docs-common {
  display: grid;
  gap: 12px;
}

.docs-common button {
  display: flex;
  justify-content: space-between;
  border: 0;
  border-bottom: 1px solid var(--rf-border-soft);
  background: transparent;
  color: var(--rf-text);
  text-align: left;
  padding: 0 0 10px;
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
  .docs-hero {
    grid-template-columns: 1fr;
  }
}
</style>
