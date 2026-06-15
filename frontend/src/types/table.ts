import type { CSSProperties, VNodeChild } from 'vue';

export type TableDataIndex = string | number | readonly (string | number)[];

export interface TableCustomRenderArgs<RecordType = object> {
  text: unknown;
  value: unknown;
  record: RecordType;
  index: number;
  column: TableColumn<RecordType>;
}

export interface TableColumn<RecordType = object> {
  title?: VNodeChild;
  dataIndex?: TableDataIndex;
  key?: string | number;
  width?: string | number;
  align?: 'left' | 'center' | 'right';
  ellipsis?: boolean;
  customRender?: (args: TableCustomRenderArgs<RecordType>) => VNodeChild;
  customCell?: (record: RecordType, index: number) => {
    class?: string;
    className?: string;
    style?: CSSProperties;
  };
}

export type TableColumnsType<RecordType = object> = TableColumn<RecordType>[];
