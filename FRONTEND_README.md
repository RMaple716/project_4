# 旅游行程规划系统 - 前端项目

> 🎉 **完整的前端项目模板已生成！**

## 📦 项目位置

```
preoject_4/
└── frontend/          ← 前端项目在此目录
    ├── src/           # 源代码
    ├── package.json   # 依赖配置
    └── README.md      # 详细文档
```

## 🚀 快速开始（3步）

### 1️⃣ 安装依赖

```bash
cd frontend
npm install
```

或使用淘宝镜像加速：
```bash
npm config set registry https://registry.npmmirror.com
npm install
```

### 2️⃣ 启动服务

**方式A：使用脚本（Windows推荐）**
```bash
start.bat
```

**方式B：手动启动**
```bash
# 终端1：启动后端
python src/index.py

# 终端2：启动前端
cd frontend
npm run dev
```

### 3️⃣ 访问应用

浏览器打开：**http://localhost:3000**

## ✨ 核心功能

- ✅ **需求提交** - 智能表单收集旅行偏好
- ✅ **任务追踪** - 实时显示行程生成进度
- ✅ **行程管理** - 创建、查看、删除行程
- ✅ **行程详情** - 时间轴展示详细安排
- ✅ **响应式设计** - 支持手机、平板、桌面

## 🛠️ 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.2.0 | UI框架 |
| TypeScript | 5.2.2 | 类型安全 |
| Vite | 5.0.8 | 构建工具 |
| Redux Toolkit | 2.0.1 | 状态管理 |
| Ant Design | 5.12.0 | UI组件库 |
| React Router | 6.21.0 | 路由管理 |
| Axios | 1.6.2 | HTTP客户端 |

## 📁 项目结构

```
frontend/
├── src/
│   ├── pages/          # 5个页面组件
│   ├── services/       # 6个API模块
│   ├── store/          # Redux状态管理
│   ├── routes/         # 路由配置
│   ├── components/     # 可复用组件
│   ├── hooks/          # 自定义Hooks
│   ├── utils/          # 工具函数
│   └── types/          # 类型定义
├── README.md           # 完整文档
├── QUICKSTART.md       # 快速上手
├── ARCHITECTURE.md     # 架构设计
└── GET_STARTED.md      # 使用说明
```

## 📖 文档导航

- 📘 **[README.md](frontend/README.md)** - 项目完整说明和技术细节
- 🚀 **[QUICKSTART.md](frontend/QUICKSTART.md)** - 5分钟快速上手指南
- 🏗️ **[ARCHITECTURE.md](frontend/ARCHITECTURE.md)** - 架构设计和数据流详解
- 📊 **[PROJECT_SUMMARY.md](frontend/PROJECT_SUMMARY.md)** - 项目生成报告
- 🎯 **[GET_STARTED.md](frontend/GET_STARTED.md)** - 详细使用说明
- 🌳 **[FILE_TREE.md](frontend/FILE_TREE.md)** - 完整文件树

## 🎯 使用流程示例

```
1. 访问首页 → 点击"新建行程"
2. 填写表单 → 目的地、天数、预算、偏好
3. 提交需求 → 自动触发任务分解
4. 查看进度 → 实时显示生成状态
5. 查看行程 → 详细的日程安排
6. 保存管理 → 随时查看和编辑
```

## 🔧 常用命令

```bash
# 开发模式（热更新）
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint
```

## 🆘 常见问题

### Q: TypeScript报错？
**A**: 这是正常的！运行 `npm install` 后错误会自动消失。

### Q: API请求失败？
**A**: 确保后端服务已启动（`http://127.0.0.1:9091`）

### Q: 端口被占用？
**A**: 修改 `vite.config.ts` 中的 `server.port`

### Q: npm install很慢？
**A**: 使用淘宝镜像：`npm config set registry https://registry.npmmirror.com`

## 📊 项目特色

- ⚡ **极速开发** - Vite构建，毫秒级热更新
- 🔒 **类型安全** - TypeScript全程覆盖
- 🎨 **美观UI** - Ant Design企业级组件
- 📱 **响应式** - 支持多端设备
- 🔄 **实时更新** - 任务进度实时轮询
- 📦 **代码分割** - 懒加载优化性能

## 🤝 团队协作

### Git工作流
```bash
git checkout -b feature/your-feature
git add .
git commit -m "feat: 添加新功能"
git push origin feature/your-feature
```

### 提交规范
- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `refactor:` 重构代码

## 🎓 学习价值

此项目展示了：
- ✅ React 18最佳实践
- ✅ TypeScript大型项目应用
- ✅ Redux Toolkit状态管理
- ✅ RESTful API封装技巧
- ✅ 组件化开发思想
- ✅ 工程化配置

## 📈 后续扩展

可根据需求添加：
- 🔐 用户认证系统
- 🗺️ 地图集成展示
- 📊 数据可视化图表
- 💬 社交分享功能
- 📱 PWA离线支持
- 🌍 多语言国际化

---

## 🎊 开始使用吧！

```bash
cd frontend
npm install
npm run dev
```

**祝你使用愉快！** ✈️🌍

---

**版本**: v1.0.0  
**最后更新**: 2026-05-22  
**状态**: ✅ 已完成并可用
