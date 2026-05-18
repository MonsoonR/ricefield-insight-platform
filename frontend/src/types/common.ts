export type RegionCode = 'all' | 'east' | 'west';

export type QualityStatus = 'normal' | 'abnormal' | 'missing' | 'empty';

export interface SelectOption<T extends string = string> {
  label: string;
  value: T;
}

export interface MetricOption {
  label: string;
  value: string;
  unit?: string;
  category?: string;
}
