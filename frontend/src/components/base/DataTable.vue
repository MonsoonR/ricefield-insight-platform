<template>
  <section class="min-w-0 overflow-hidden rounded-[var(--rf-radius-lg)] border border-[var(--rf-border-soft)] bg-[var(--rf-surface)] shadow-[var(--rf-shadow-soft)]">
    <header v-if="title || $slots.extra" class="flex items-start justify-between gap-3.5 border-b border-[var(--rf-border-soft)] px-5 py-4">
      <div>
        <h2 v-if="title" class="m-0 text-base font-extrabold text-[var(--rf-text)]">{{ title }}</h2>
        <p v-if="description" class="mt-1 text-xs text-[var(--rf-text-muted)]">{{ description }}</p>
      </div>
      <slot name="extra" />
    </header>

    <div class="p-0">
      <ErrorState v-if="error" :message="error" compact />
      <LoadingState v-else-if="loading" :rows="4" :height="180" />
      <EmptyState v-else-if="dataSource.length === 0" compact :description="emptyText" />
      <template v-else>
        <Table
          class="min-w-[var(--rf-table-min-width)] text-[13px] text-[var(--rf-text)]"
          :style="tableRootStyle"
        >
          <TableHeader class="bg-[var(--rf-surface-muted)]">
            <TableRow class="hover:bg-transparent">
              <TableHead
                v-for="column in columns"
                :key="columnKey(column)"
                class="h-11 whitespace-nowrap px-3 text-[13px] font-extrabold text-[var(--rf-text-muted)]"
                :class="headClass(column)"
                :style="columnStyle(column)"
              >
                {{ column.title }}
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow
              v-for="(record, rowIndex) in pagedRows"
              :key="getRowKey(record, absoluteRowIndex(rowIndex))"
              class="min-h-12 border-[var(--rf-border-soft)] hover:bg-[color-mix(in_srgb,var(--rf-primary-soft)_46%,white)]"
              :class="rowClassName?.(record, absoluteRowIndex(rowIndex))"
            >
              <TableCell
                v-for="column in columns"
                :key="columnKey(column)"
                class="h-12 whitespace-nowrap px-3"
                :class="cellClass(column, record, absoluteRowIndex(rowIndex))"
                :style="cellStyle(column, record, absoluteRowIndex(rowIndex))"
              >
                <BodyCellContent
                  :column="column"
                  :record="record"
                  :row-index="absoluteRowIndex(rowIndex)"
                  :text="cellValue(record, column)"
                />
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>

        <footer v-if="showPagination" class="flex flex-wrap items-center justify-between gap-3 border-t border-[var(--rf-border-soft)] px-4 py-3">
          <span class="text-xs text-[var(--rf-text-muted)]">{{ totalText }}</span>
          <div class="flex items-center gap-2">
            <Button variant="outline" size="sm" :disabled="currentPage <= 1" @click="currentPage -= 1">
              上一页
            </Button>
            <span class="text-xs font-semibold text-[var(--rf-text-muted)]">
              {{ currentPage }} / {{ totalPages }}
            </span>
            <Button variant="outline" size="sm" :disabled="currentPage >= totalPages" @click="currentPage += 1">
              下一页
            </Button>
          </div>
        </footer>
      </template>
    </div>
  </section>
</template>

<script setup lang="ts">
import { Comment, computed, defineComponent, h, ref, useSlots, watch } from 'vue';
import type { CSSProperties, PropType, VNode } from 'vue';

import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import type { TableColumn, TableColumnsType } from '@/types/table';

import EmptyState from './EmptyState.vue';
import ErrorState from './ErrorState.vue';
import LoadingState from './LoadingState.vue';

type TableRecord = object;
type PaginationConfig = Record<string, unknown> & {
  pageSize?: number;
  showTotal?: (total: number) => string;
};

const props = withDefaults(
  defineProps<{
    title?: string;
    description?: string;
    columns: TableColumnsType<TableRecord>;
    dataSource: readonly TableRecord[];
    rowKey?: string | ((record: TableRecord) => string);
    loading?: boolean;
    error?: string;
    emptyText?: string;
    pagination?: false | PaginationConfig;
    scroll?: Record<string, string | number | true>;
    rowClassName?: (record: TableRecord, index: number) => string;
  }>(),
  {
    title: '',
    description: '',
    rowKey: 'id',
    loading: false,
    error: '',
    emptyText: '暂无数据',
    pagination: false,
    scroll: undefined,
    rowClassName: undefined,
  },
);

const slots = useSlots();
const currentPage = ref(1);

const pageSize = computed(() =>
  props.pagination === false ? props.dataSource.length || 1 : Number(props.pagination?.pageSize) || 10,
);

const totalPages = computed(() => Math.max(1, Math.ceil(props.dataSource.length / pageSize.value)));
const showPagination = computed(() => props.pagination !== false && props.dataSource.length > pageSize.value);
const pagedRows = computed(() => {
  if (props.pagination === false) {
    return props.dataSource;
  }
  const start = (currentPage.value - 1) * pageSize.value;
  return props.dataSource.slice(start, start + pageSize.value);
});
const totalText = computed(() => {
  if (props.pagination !== false && props.pagination?.showTotal) {
    return props.pagination.showTotal(props.dataSource.length);
  }
  return `共 ${props.dataSource.length} 条`;
});
const tableMinWidth = computed(() => {
  const x = props.scroll?.x;
  if (typeof x === 'number') {
    return `${x}px`;
  }
  if (typeof x === 'string') {
    return x;
  }
  return '100%';
});
const tableRootStyle = computed<CSSProperties>(() => {
  const style: CSSProperties = {
    '--rf-table-min-width': tableMinWidth.value,
  } as CSSProperties;
  const y = props.scroll?.y;
  if (typeof y === 'number') {
    style.maxHeight = `${y}px`;
  } else if (typeof y === 'string') {
    style.maxHeight = y;
  }
  return style;
});

watch(
  () => [props.dataSource.length, pageSize.value],
  () => {
    currentPage.value = Math.min(currentPage.value, totalPages.value);
    if (currentPage.value < 1) {
      currentPage.value = 1;
    }
  },
);

const BodyCellContent = defineComponent({
  props: {
    column: {
      type: Object as PropType<TableColumn<TableRecord>>,
      required: true,
    },
    record: {
      type: Object as PropType<TableRecord>,
      required: true,
    },
    rowIndex: {
      type: Number,
      required: true,
    },
    text: {
      type: null as unknown as PropType<any>,
      default: undefined,
    },
  },
  setup(cellProps) {
    return () => {
      const slotNodes = slots.bodyCell?.({
        column: cellProps.column,
        record: cellProps.record,
        index: cellProps.rowIndex,
        text: cellProps.text,
      });
      if (hasRenderableNodes(slotNodes)) {
        return slotNodes;
      }
      if (cellProps.column.customRender) {
        return cellProps.column.customRender({
          text: cellProps.text,
          value: cellProps.text,
          record: cellProps.record,
          index: cellProps.rowIndex,
          column: cellProps.column,
        });
      }
      return h('span', { class: cellProps.column.ellipsis ? 'block max-w-full truncate' : '' }, formatCellValue(cellProps.text));
    };
  },
});

function hasRenderableNodes(nodes?: VNode[]) {
  return Boolean(nodes?.some((node) => node.type !== Comment));
}

function columnKey(column: TableColumn<TableRecord>) {
  return String(column.key ?? column.dataIndex ?? column.title ?? 'column');
}

function columnStyle(column: TableColumn<TableRecord>): CSSProperties {
  if (!column.width) {
    return {};
  }
  return {
    width: typeof column.width === 'number' ? `${column.width}px` : column.width,
    minWidth: typeof column.width === 'number' ? `${column.width}px` : column.width,
  };
}

function headClass(column: TableColumn<TableRecord>) {
  return {
    'text-center': column.align === 'center',
    'text-right': column.align === 'right',
  };
}

function cellClass(column: TableColumn<TableRecord>, record: TableRecord, index: number) {
  const custom = column.customCell?.(record, index);
  return [
    {
      'text-center': column.align === 'center',
      'text-right': column.align === 'right',
      'max-w-0': column.ellipsis,
    },
    custom?.class,
    custom?.className,
  ];
}

function cellStyle(column: TableColumn<TableRecord>, record: TableRecord, index: number) {
  const customStyle = column.customCell?.(record, index)?.style;
  return customStyle ? [columnStyle(column), customStyle] : columnStyle(column);
}

function cellValue(record: TableRecord, column: TableColumn<TableRecord>) {
  const dataIndex = column.dataIndex;
  if (Array.isArray(dataIndex)) {
    return dataIndex.reduce<unknown>((current, key) => {
      if (current && typeof current === 'object') {
        return (current as Record<string | number, unknown>)[key];
      }
      return undefined;
    }, record);
  }
  if (typeof dataIndex === 'string' || typeof dataIndex === 'number') {
    return (record as Record<string | number, unknown>)[dataIndex];
  }
  return undefined;
}

function absoluteRowIndex(rowIndex: number) {
  if (props.pagination === false) {
    return rowIndex;
  }
  return (currentPage.value - 1) * pageSize.value + rowIndex;
}

function formatCellValue(value: unknown) {
  if (value === null || value === undefined || value === '') {
    return '--';
  }
  return String(value);
}

function getRowKey(record: TableRecord, index: number) {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(record);
  }
  return String((record as Record<string, unknown>)[props.rowKey] ?? index);
}
</script>
