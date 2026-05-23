# 旅游行程规划前端系统

基于 React + TypeScript + Vite 构建的现代化前端应用。

## 技术栈

- **框架**: React 18
- **语言**: TypeScript
- **构建工具**: Vite
- **路由**: React Router v6
- **状态管理**: Redux Toolkit + React-Redux
- **UI组件库**: Ant Design 5
- **HTTP客户端**: Axios
- **日期处理**: Day.js

## 项目结构

```
frontend/
├── src/
│   ├── components/        # 可复用组件
│   ├── pages/            # 页面组件
│   │   ├── Home.tsx              # 首页
│   │   ├── RequirementForm.tsx   # 需求表单
│   │   ├── ItineraryList.tsx     # 行程列表
│   │   ├── ItineraryDetail.tsx   # 行程详情
│   │   └── TaskStatus.tsx        # 任务状态
│   ├── services/         # API服务层
│   │   ├── api.ts                # Axios配置
│   │   ├── requirementApi.ts     # 需求API
│   │   ├── taskApi.ts            # 任务API
│   │   ├── itineraryApi.ts       # 行程API
│   │   ├── validationApi.ts      # 验证API
│   │   └── staticDataApi.ts      # 静态数据API
│   ├── store/            # Redux状态管理
│   │   ├── index.ts              # Store配置
│   │   └── slices/               # Redux Slices
│   │       ├── requirementSlice.ts
│   │       ├── itinerarySlice.ts
│   │       └── uiSlice.ts
│   ├── routes/           # 路由配置
│   │   └── index.tsx
│   ├── App.tsx           # 主应用组件
│   ├── main.tsx          # 入口文件
│   └── index.css         # 全局样式
├── index.html            # HTML模板
├── package.json          # 依赖配置
├── vite.config.ts        # Vite配置
├── tsconfig.json         # TypeScript配置
└── README.md             # 项目文档
```

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

应用将在 `http://localhost:3000` 启动

### 3. 构建生产版本

```bash
npm run build
```

### 4. 预览生产构建

```bash
npm run preview
```

## 功能特性

### ✅ 已实现功能

1. **首页** - 展示系统概览和快捷入口
2. **需求提交** - 填写旅行偏好和需求
3. **任务追踪** - 实时显示行程生成进度
4. **行程列表** - 查看和管理所有行程
5. **行程详情** - 展示详细的日程安排
6. **响应式设计** - 支持移动端和桌面端

### 📋 API集成

前端已与后端API完全对接，包括：

- ✅ 用户需求提交和解析
- ✅ 任务分解和状态追踪
- ✅ 行程创建、查询、更新、删除
- ✅ 时间冲突检测
- ✅ 静态数据获取（景点、城市等）

## 开发指南

### 添加新页面

1. 在 `src/pages/` 创建新组件
2. 在 `src/routes/index.tsx` 添加路由配置
3. 在导航菜单中添加链接（如需要）

### 添加新的API接口

1. 在 `src/services/` 创建新的API文件
2. 定义TypeScript接口类型
3. 导出API方法

### 状态管理

使用Redux Toolkit管理全局状态：

```typescript
// 在组件中使用
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';

const data = useSelector((state: RootState) => state.requirement);
dispatch(setLoading(true));
```

## 代理配置

开发环境下，Vite已配置API代理：

```typescript
// vite.config.ts
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:9091',
      changeOrigin: true,
    }
  }
}
```

所有 `/api/v1/*` 的请求会自动转发到后端服务。

## 代码规范

- 使用TypeScript严格模式
- 遵循React Hooks最佳实践
- 组件采用函数式编程
- 使用ESLint和Prettier保持代码风格一致

## 浏览器支持

- Chrome (最新)
- Firefox (最新)
- Safari (最新)
- Edge (最新)

## 常见问题

### Q1: 如何修改后端API地址？

修改 `vite.config.ts` 中的 `proxy.target` 配置。

### Q2: 如何添加认证token？

在 `src/services/api.ts` 的请求拦截器中已预留token添加逻辑。

### Q3: 如何自定义主题？

使用Ant Design的主题配置，参考官方文档：https://ant.design/docs/react/customize-theme

## 更新日志

### v1.0.0 (2026-05-22)
- ✨ 初始版本发布
- ✨ 完整的前端架构搭建
- ✨ 5个核心页面实现
- ✨ Redux状态管理
- ✨ API完整对接

---

**最后更新**: 2026-05-22  
**版本**: v1.0.0
