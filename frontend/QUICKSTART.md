# 前端项目快速开始指南

## 📦 安装依赖

```bash
cd frontend
npm install
```

如果npm下载速度慢，可以使用淘宝镜像：

```bash
npm config set registry https://registry.npmmirror.com
npm install
```

## 🚀 启动开发环境

### 第一步：启动后端服务

在新终端中启动后端服务：

```bash
cd ..
python src/index.py
```

后端服务将在 `http://127.0.0.1:9091` 启动

### 第二步：启动前端开发服务器

在另一个终端中启动前端：

```bash
cd frontend
npm run dev
```

前端应用将在 `http://localhost:3000` 启动

## 🎯 使用流程

1. **访问首页** - 打开浏览器访问 `http://localhost:3000`
2. **新建行程** - 点击"新建行程"按钮
3. **填写需求** - 填写旅行目的地、天数、预算等信息
4. **提交需求** - 点击提交，系统自动进行任务分解
5. **查看进度** - 实时查看行程生成进度
6. **查看行程** - 生成完成后查看详细行程安排

## 📁 项目结构说明

```
frontend/
├── src/
│   ├── components/        # 可复用UI组件
│   ├── pages/            # 页面级组件（5个核心页面）
│   ├── services/         # API接口封装
│   ├── store/            # Redux状态管理
│   ├── routes/           # 路由配置
│   ├── hooks/            # 自定义Hooks
│   ├── utils/            # 工具函数
│   ├── types/            # TypeScript类型定义
│   └── App.tsx           # 主应用组件
├── package.json          # 项目依赖
├── vite.config.ts        # Vite配置（含API代理）
└── README.md             # 详细文档
```

## 🔧 常用命令

```bash
# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint
```

## 🌐 API代理配置

开发环境下，所有 `/api` 请求会自动转发到后端：

- 前端地址: `http://localhost:3000`
- 后端地址: `http://127.0.0.1:9091`
- 代理配置: `vite.config.ts`

## 📱 响应式设计

系统支持以下设备：

- ✅ 桌面端 (≥1200px)
- ✅ 平板端 (768px - 1199px)
- ✅ 移动端 (<768px)

## 🐛 常见问题

### Q1: npm install 失败？

尝试清除缓存后重新安装：
```bash
npm cache clean --force
npm install
```

### Q2: 端口3000被占用？

修改 `vite.config.ts` 中的 `server.port` 配置

### Q3: API请求失败？

1. 确认后端服务已启动
2. 检查浏览器控制台的网络请求
3. 确认代理配置正确

### Q4: 如何修改后端API地址？

编辑 `vite.config.ts`:
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://你的后端地址',
      changeOrigin: true,
    }
  }
}
```

## 📚 学习资源

- [React官方文档](https://react.dev/)
- [TypeScript手册](https://www.typescriptlang.org/docs/)
- [Vite指南](https://vitejs.dev/guide/)
- [Ant Design组件库](https://ant.design/)
- [Redux Toolkit](https://redux-toolkit.js.org/)

## 🤝 团队协作

### Git工作流

```bash
# 创建功能分支
git checkout -b feature/your-feature

# 提交代码
git add .
git commit -m "feat: 添加新功能"

# 推送到远程
git push origin feature/your-feature
```

### 提交规范

遵循 Conventional Commits:
- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `style:` 代码格式
- `refactor:` 重构代码
- `test:` 测试相关

---

**提示**: 首次运行建议先阅读 `README.md` 了解完整的项目架构和功能。
