import type { ThemeConfig } from 'ant-design-vue/es/config-provider/context';

export const themeConfig: ThemeConfig = {
  token: {
    colorPrimary: '#15905d',
    colorSuccess: '#16a36a',
    colorWarning: '#ea580c',
    colorError: '#dc2626',
    colorInfo: '#2878d7',
    colorTextBase: '#1f2937',
    colorBgBase: '#f6f8f7',
    colorBgContainer: '#FFFFFF',
    colorBorder: '#e5ece7',
    colorBorderSecondary: '#edf2ef',
    borderRadius: 6,
    borderRadiusLG: 12,
    boxShadow: '0 1px 2px rgba(15, 56, 37, 0.04), 0 1px 3px rgba(15, 56, 37, 0.06)',
    boxShadowSecondary: '0 1px 2px rgba(15, 56, 37, 0.03), 0 1px 2px rgba(15, 56, 37, 0.04)',
    fontFamily:
      '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif',
    wireframe: false,
  },
  components: {
    Button: {
      colorPrimaryHover: '#0b7b4d',
      controlHeight: 36,
    },
  },
};
