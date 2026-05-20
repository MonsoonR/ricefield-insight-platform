import {
  Button,
  Badge,
  Card,
  ConfigProvider,
  DatePicker,
  Divider,
  Drawer,
  Form,
  Empty,
  Input,
  Layout,
  Menu,
  Pagination,
  Progress,
  Result,
  Select,
  Segmented,
  Skeleton,
  Space,
  Statistic,
  Switch,
  Tabs,
  Table,
  Tag,
  Tooltip,
} from 'ant-design-vue';
import { createPinia } from 'pinia';
import { createApp } from 'vue';

import App from './App.vue';
import router from './router';
import 'ant-design-vue/dist/reset.css';
import './styles/global.css';

createApp(App)
  .use(createPinia())
  .use(router)
  .use(Button)
  .use(Badge)
  .use(Card)
  .use(ConfigProvider)
  .use(DatePicker)
  .use(Divider)
  .use(Drawer)
  .use(Form)
  .use(Empty)
  .use(Input)
  .use(Layout)
  .use(Menu)
  .use(Pagination)
  .use(Progress)
  .use(Result)
  .use(Select)
  .use(Segmented)
  .use(Skeleton)
  .use(Space)
  .use(Statistic)
  .use(Switch)
  .use(Tabs)
  .use(Table)
  .use(Tag)
  .use(Tooltip)
  .mount('#app');
