import { defineStore } from 'pinia';

export const useAppStore = defineStore('app', {
  state: () => ({
    collapsed: false,
    platformTitle: '稻田智研平台',
  }),
  actions: {
    setCollapsed(value: boolean) {
      this.collapsed = value;
    },
  },
});
