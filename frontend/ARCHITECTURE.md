# 前端项目架构设计文档

## 📐 整体架构

```
┌─────────────────────────────────────────┐
│          用户界面层 (UI Layer)           │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ │
│  │  Home   ││Requirement││Itinerary │ │
│  │  Page   ││   Form    ││  Pages   │ │
│  └─────────┘ └──────────┘ └──────────┘ │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       状态管理层 (State Management)      │
│  ┌──────────────────────────────────┐   │
│  │     Redux Toolkit Store          │   │
│  │  - requirementSlice              │   │
│  │  - itinerarySlice                │   │
│  │  - uiSlice                       │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│        服务层 (Service Layer)            │
│  ┌──────────────────────────────────┐   │
│  │     API Services (Axios)         │   │
│  │  - requirementApi                │   │
│  │  - taskApi                       │   │
│  │  - itineraryApi                  │   │
│  │  - validationApi                 │   │
│  │  - staticDataApi                 │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│        后端API (Backend API)             │
│     http://127.0.0.1:9091/api/v1        │
└─────────────────────────────────────────┘
```

## 🗂️ 目录结构详解

### 1. src/pages/ - 页面组件

**职责**: 完整的页面级组件，包含业务逻辑和UI展示

- **Home.tsx** - 首页
  - 功能: 系统概览、快捷入口
  - 路由: `/`

- **RequirementForm.tsx** - 需求表单页
  - 功能: 收集用户旅行需求
  - 路由: `/requirement`
  - 交互: 提交后自动触发任务分解

- **ItineraryList.tsx** - 行程列表页
  - 功能: 展示用户所有行程
  - 路由: `/itineraries`
  - 操作: 查看、删除行程

- **ItineraryDetail.tsx** - 行程详情页
  - 功能: 展示详细行程安排
  - 路由: `/itinerary/:id`
  - 展示: 按天分组的Timeline时间轴

- **TaskStatus.tsx** - 任务状态页
  - 功能: 实时显示任务进度
  - 路由: `/task/:taskId`
  - 特性: 3秒轮询更新状态

### 2. src/services/ - API服务层

**职责**: 封装所有后端API调用，提供类型安全的接口

#### api.ts - Axios配置
```typescript
- baseURL: /api/v1
- timeout: 30000ms
- 请求拦截器: 自动添加token
- 响应拦截器: 统一错误处理
```

#### requirementApi.ts - 需求相关API
```typescript
- submit()      // 提交需求
- parse()       // 解析需求文本
- getById()     // 获取需求详情
```

#### taskApi.ts - 任务相关API
```typescript
- decompose()   // 任务分解
- getById()     // 获取任务状态
- update()      // 更新任务结果
```

#### itineraryApi.ts - 行程相关API
```typescript
- create()      // 创建行程
- getById()     // 获取行程详情
- update()      // 更新行程
- delete()      // 删除行程
- getByUser()   // 获取用户行程列表
```

#### validationApi.ts - 验证相关API
```typescript
- checkTimeConflict()  // 时间冲突检测
- validateItinerary()  // 完整行程校验
```

#### staticDataApi.ts - 静态数据API
```typescript
- getAttractions()       // 获取所有景点
- getAttractionsByCity() // 获取城市景点
- getCities()            // 获取城市列表
- getLocations()         // 获取地点库
```

### 3. src/store/ - 状态管理

**职责**: 使用Redux Toolkit管理全局状态

#### store/index.ts - Store配置
```typescript
reducer: {
  requirement: 需求状态
  itinerary:   行程状态
  ui:          UI状态
}
```

#### slices/requirementSlice.ts
```typescript
state: {
  currentRequirement: Requirement | null
  requirementId: string | null
  loading: boolean
  error: string | null
}

actions:
  - setRequirement()
  - setRequirementId()
  - setLoading()
  - setError()
  - clearRequirement()
```

#### slices/itinerarySlice.ts
```typescript
state: {
  currentItinerary: Itinerary | null
  itineraries: Itinerary[]
  loading: boolean
  error: string | null
}

actions:
  - setCurrentItinerary()
  - setItineraries()
  - addItinerary()
  - updateItinerary()
  - deleteItinerary()
  - setLoading()
  - setError()
```

#### slices/uiSlice.ts
```typescript
state: {
  theme: 'light' | 'dark'
  sidebarCollapsed: boolean
  loading: boolean
}

actions:
  - toggleTheme()
  - setTheme()
  - toggleSidebar()
  - setLoading()
```

### 4. src/routes/ - 路由配置

**职责**: 定义应用的路由结构和懒加载

```typescript
routes = [
  { path: '/', element: <Home /> },
  { path: '/requirement', element: <RequirementForm /> },
  { path: '/itineraries', element: <ItineraryList /> },
  { path: '/itinerary/:id', element: <ItineraryDetail /> },
  { path: '/task/:taskId', element: <TaskStatus /> }
]
```

### 5. src/components/ - 可复用组件

**职责**: 提供可在多个页面复用的UI组件

- **SummaryCard.tsx** - 摘要卡片组件
  - 展示: 目的地、天数、预算、人数

### 6. src/hooks/ - 自定义Hooks

**职责**: 封装可复用的React逻辑

- **useLocalStorage()** - localStorage持久化
- **useWindowSize()** - 窗口大小监听
- **useAsync()** - 异步请求管理

### 7. src/utils/ - 工具函数

**职责**: 提供通用的辅助函数

#### helpers.ts
```typescript
- formatDate()        // 格式化日期
- formatTime()        // 格式化时间
- formatMoney()       // 格式化金额
- daysBetween()       // 计算天数差
- generateId()        // 生成唯一ID
- debounce()          // 防抖函数
- throttle()          // 节流函数
- deepClone()         // 深拷贝
- getFromStorage()    // 读取localStorage
- saveToStorage()     // 保存localStorage
- removeFromStorage() // 删除localStorage
```

### 8. src/types/ - 类型定义

**职责**: 定义TypeScript接口和类型

```typescript
- ApiResponse<T>     // API响应格式
- PaginationParams   // 分页参数
- User               // 用户信息
- Attraction         // 景点信息
- Hotel              // 酒店信息
- Restaurant         // 餐厅信息
- Transport          // 交通信息
```

## 🔄 数据流示例

### 场景: 用户提交旅行需求

```
1. 用户在 RequirementForm 填写表单
         ↓
2. 点击"提交"按钮
         ↓
3. 调用 requirementApi.submit()
         ↓
4. Axios发送POST请求到后端
         ↓
5. 后端返回 response (code: 200, data: {...})
         ↓
6.  dispatch(setRequirement(data))
         ↓
7. Redux Store更新状态
         ↓
8. 自动调用 taskApi.decompose()
         ↓
9. 导航到 TaskStatus 页面
         ↓
10. 每3秒轮询任务状态
         ↓
11. 任务完成后导航到 ItineraryDetail
```

## 🎨 UI组件库集成

### Ant Design 5.x

**已使用的组件**:
- Layout, Menu, Header, Content, Footer - 布局
- Card, List, Timeline - 数据展示
- Form, Input, Select, DatePicker - 表单
- Button, Space, Tag - 通用
- Typography - 文本
- Message, Alert - 反馈
- Spin, Progress - 加载
- Descriptions, Statistic - 数据展示
- Empty - 空状态

**主题定制**:
```typescript
// 在 main.tsx 中配置
<ConfigProvider locale={zhCN}>
  <App />
</ConfigProvider>
```

## 🚀 性能优化

### 1. 代码分割
```typescript
// routes/index.tsx 中使用懒加载
const Home = lazy(() => import('../pages/Home'));
```

### 2. API代理
```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:9091',
      changeOrigin: true,
    }
  }
}
```

### 3. 状态管理优化
- 使用 Redux Toolkit 的 Immer 进行不可变更新
- 细粒度的slice划分
- 避免不必要的重渲染

## 🔐 安全考虑

### 1. Token认证
```typescript
// services/api.ts
config.headers.Authorization = `Bearer ${token}`;
```

### 2. XSS防护
- React自动转义输出
- 避免使用 dangerouslySetInnerHTML

### 3. CSRF防护
- 使用SameSite Cookie
- 验证请求来源

## 📱 响应式设计

### 断点设置
```css
xs:  < 576px   (手机)
sm:  ≥ 576px   (小屏平板)
md:  ≥ 768px   (平板)
lg:  ≥ 992px   (桌面)
xl:  ≥ 1200px  (大桌面)
xxl: ≥ 1600px  (超大屏幕)
```

### Grid布局
```typescript
<List
  grid={{ 
    gutter: 16, 
    xs: 1, sm: 2, md: 2, lg: 3, xl: 3, xxl: 4 
  }}
/>
```

## 🧪 测试策略（待实现）

### 单元测试
- Jest + React Testing Library
- 测试组件渲染
- 测试Hooks逻辑

### 集成测试
- Cypress
- 测试用户流程
- 测试API交互

### E2E测试
- 完整用户旅程
- 跨浏览器测试

## 📊 监控与日志（待实现）

### 错误监控
- Sentry集成
- 捕获运行时错误
- 上报异常信息

### 性能监控
- Web Vitals
- LCP, FID, CLS指标
- 慢查询分析

## 🔄 持续集成/部署（待实现）

### CI/CD流程
```yaml
build → test → deploy
```

### 自动化
- GitHub Actions
- 自动运行测试
- 自动部署到服务器

---

**文档版本**: v1.0.0  
**最后更新**: 2026-05-22
