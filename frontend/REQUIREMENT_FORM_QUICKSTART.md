# 🚀 需求表单页面 - 快速启动指南

## ⚡ 3分钟快速体验

### 第一步：安装依赖（如果还未安装）

```bash
cd frontend
npm install
```

> 💡 如果下载速度慢，使用淘宝镜像：
> ```bash
> npm config set registry https://registry.npmmirror.com
> npm install
> ```

### 第二步：启动后端服务

在新终端中运行：

```bash
cd ..
python src/index.py
```

确认看到类似输出：
```
INFO:     Uvicorn running on http://127.0.0.1:9091
INFO:     Application startup complete.
```

### 第三步：启动前端开发服务器

在另一个新终端中运行：

```bash
cd frontend
npm run dev
```

确认看到类似输出：
```
VITE v5.0.8  ready in 500 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

### 第四步：访问需求表单

浏览器打开：**http://localhost:3000/requirement**

---

## 📝 测试填写示例

### 示例1：北京文化之旅

```
目的地城市：北京
出发日期：2026-06-15
旅行天数：4
出行人数：2
总预算：6000
出行类型：家庭出游
旅行偏好：历史古迹、文化体验、美食探索
特殊需求：希望参观故宫和长城，有老人同行需要无障碍设施
```

**点击提交后**：
1. ✅ 看到"需求提交成功！"提示
2. ✅ 看到"正在智能规划行程..."加载提示
3. ✅ 自动跳转到任务状态页面
4. ✅ 实时显示进度条增长
5. ✅ 完成后显示"行程生成成功！"
6. ✅ 可以点击"查看行程"按钮

---

## 🎯 核心功能演示

### 1. 表单验证

**尝试以下操作**：

- 不填城市名称直接提交 → 看到红色错误提示
- 输入单个字的城市名 → 看到"至少2个字符"提示
- 选择过去的日期 → 日期被禁用无法选择
- 预算输入500 → 看到"最低预算1000元"提示

### 2. 偏好选择

**操作步骤**：
1. 点击"旅行偏好"下拉框
2. 选择多个标签（如：历史古迹、美食探索）
3. 观察下方实时显示已选标签
4. 点击标签上的×可以取消选择

### 3. 预算格式化

**输入体验**：
- 输入：5000
- 显示：¥ 5,000
- 自动添加千分位分隔符

### 4. 响应式布局

**调整浏览器窗口大小**：
- 宽屏（>1200px）：三列布局
- 中屏（768-1199px）：双列布局
- 窄屏（<768px）：单列布局

---

## 🔍 调试技巧

### 查看API请求

1. 打开浏览器开发者工具（F12）
2. 切换到 **Network** 标签
3. 填写表单并提交
4. 观察两个请求：
   - `POST /api/v1/requirement/submit` - 提交需求
   - `POST /api/v1/task/decompose` - 任务分解

### 查看控制台日志

在开发者工具的 **Console** 标签中可以看到：
```javascript
提交需求: {city_name: "北京", travel_days: 4, ...}
```

### 查看Redux状态

如果安装了Redux DevTools扩展：
1. 打开扩展面板
2. 观察 `requirement` slice 的状态变化
3. 查看 `loading` 状态的切换

---

## 🐛 常见问题解决

### 问题1：npm install 失败

**错误信息**：
```
npm ERR! ERESOLVE unable to resolve dependency tree
```

**解决方法**：
```bash
npm cache clean --force
npm install --legacy-peer-deps
```

### 问题2：端口3000被占用

**错误信息**：
```
Port 3000 is in use
```

**解决方法**：
修改 `vite.config.ts`：
```typescript
server: {
  port: 3001,  // 改为其他端口
  ...
}
```

### 问题3：后端连接失败

**错误信息**：
```
POST http://localhost:3000/api/v1/requirement/submit 500
```

**检查清单**：
- [ ] 后端服务是否启动？
- [ ] 后端是否在9091端口运行？
- [ ] 防火墙是否阻止连接？

**解决方法**：
```bash
# 确认后端进程
netstat -ano | findstr :9091

# 重新启动后端
python src/index.py
```

### 问题4：TypeScript报错

**错误信息**：
```
找不到模块"antd"或其相应的类型声明
```

**原因**：依赖尚未安装

**解决方法**：
```bash
npm install
```

安装完成后错误会自动消失。

### 问题5：提交后没有跳转

**可能原因**：
- 任务分解API返回失败
- 网络连接问题

**排查步骤**：
1. 检查Network面板的decompose请求
2. 查看响应状态码
3. 检查后端日志

---

## 📱 移动端测试

### 使用Chrome DevTools模拟

1. 按 F12 打开开发者工具
2. 点击设备工具栏图标（或 Ctrl+Shift+M）
3. 选择设备型号（如 iPhone 12 Pro）
4. 刷新页面测试

### 真机测试

1. 确保手机和电脑在同一WiFi网络
2. 修改 `vite.config.ts`：
   ```typescript
   server: {
     host: '0.0.0.0',  // 允许外部访问
     port: 3000,
   }
   ```
3. 重启开发服务器
4. 手机浏览器访问：`http://你的电脑IP:3000/requirement`

---

## ✅ 验收检查清单

完成以下检查确认功能正常：

### 基础功能
- [ ] 页面可以正常访问
- [ ] 所有字段正确显示
- [ ] 图标和样式正常
- [ ] 响应式布局适配

### 表单验证
- [ ] 必填项验证生效
- [ ] 数值范围验证生效
- [ ] 日期选择限制生效
- [ ] 错误提示清晰

### 交互体验
- [ ] 偏好标签可以选择和取消
- [ ] 预算金额格式化显示
- [ ] Tooltip提示正常显示
- [ ] 重置功能正常工作

### API集成
- [ ] 提交请求发送到后端
- [ ] 收到正确的响应
- [ ] 自动触发任务分解
- [ ] 正确跳转到状态页

### 用户体验
- [ ] 加载状态有提示
- [ ] 成功消息友好
- [ ] 错误消息明确
- [ ] 整体流程流畅

---

## 🎓 学习要点

通过这个项目你可以学到：

1. **React表单处理**
   - Ant Design Form组件使用
   - 表单验证规则配置
   - 受控组件与非受控组件

2. **TypeScript类型安全**
   - 接口定义
   - 类型推断
   - 泛型应用

3. **状态管理**
   - Redux Toolkit使用
   - useDispatch和useSelector
   - Slice设计模式

4. **API集成**
   - Axios封装
   - 拦截器配置
   - 错误处理

5. **响应式设计**
   - Ant Design栅格系统
   - 媒体查询
   - 移动优先设计

---

## 📚 相关文档

- 📘 [完整使用说明](REQUIREMENT_FORM_GUIDE.md)
- 🧪 [测试指南](REQUIREMENT_FORM_TEST.md)
- 📊 [开发总结](REQUIREMENT_FORM_SUMMARY.md)
- 🏗️ [项目架构](ARCHITECTURE.md)

---

## 🎉 开始体验吧！

```bash
# 一键启动（Windows）
start.bat

# 或手动启动
npm run dev
```

**祝你使用愉快！** ✈️🌍

---

**最后更新**: 2026-05-23  
**版本**: v1.0.0
