# 用户需求输入页面使用说明

## 📋 页面功能

用户需求输入页面是旅游行程规划系统的入口，用户在此页面填写旅行偏好和需求，系统将基于这些信息智能生成个性化行程。

## ✨ 核心特性

### 1. 完整的表单字段

#### 基本信息（必填）
- **目的地城市** - 您想要前往的旅游城市
- **出发日期** - 旅行开始的日期（不能选择过去的日期）
- **旅行天数** - 1-30天的范围选择
- **出行人数** - 包括您在内的总人数（1-20人）
- **总预算** - 包含所有费用的总预算（最低1000元）

#### 旅行偏好（可选）
- **出行类型** - 家庭出游、情侣出行、朋友同行、独自旅行、商务出差
- **旅行偏好** - 多选标签，最多选择5个：
  - 🏛️ 历史古迹
  - 🏞️ 自然风光
  - 🍜 美食探索
  - 🛍️ 购物休闲
  - 🎭 文化体验
  - 🚴 户外运动
  - 📸 摄影打卡
  - 👨‍👩‍👧‍👦 亲子活动
  - 🌃 夜生活
  - ♨️ 温泉度假

#### 特殊需求（可选）
- 文本输入框，最多500字符
- 可以说明无障碍设施、饮食禁忌、儿童友好等特殊要求

### 2. 用户体验优化

#### 视觉设计
- ✅ 清晰的分组布局（基本信息、旅行偏好）
- ✅ 图标辅助理解（每个字段都有对应图标）
- ✅ 实时显示已选择的偏好标签
- ✅ 响应式设计，支持移动端和桌面端

#### 交互体验
- ✅ 表单验证提示（必填项标记、错误提示）
- ✅ Tooltip提示信息（鼠标悬停查看详细说明）
- ✅ 预算金额格式化显示（¥ 5,000）
- ✅ 日期选择器限制（不能选择过去日期）
- ✅ 加载状态提示（提交时显示loading）
- ✅ 成功/失败消息反馈

#### 智能引导
- ✅ 温馨提示Alert组件
- ✅ 字段级别的tooltip说明
- ✅ 底部提示语鼓励详细填写
- ✅ 示例placeholder文本

### 3. 数据处理流程

```
用户填写表单
    ↓
前端验证（必填项、格式等）
    ↓
提交到后端 API (/api/v1/requirement/submit)
    ↓
获取 requirement_id
    ↓
自动调用任务分解 API (/api/v1/task/decompose)
    ↓
跳转到任务状态页面
    ↓
实时显示行程生成进度
```

## 🔧 技术实现

### 使用的Ant Design组件

| 组件 | 用途 |
|------|------|
| Form | 表单容器和验证 |
| Input | 城市名称输入 |
| DatePicker | 日期选择 |
| InputNumber | 数字输入（天数、人数、预算） |
| Select | 下拉选择（出行类型、偏好） |
| TextArea | 多行文本输入（特殊需求） |
| Button | 提交和重置按钮 |
| Card | 卡片容器 |
| Alert | 提示信息 |
| Tag | 偏好标签展示 |
| Divider | 分隔线 |
| Row/Col | 栅格布局 |
| Space | 间距控制 |
| Tooltip | 提示气泡 |

### 状态管理

```typescript
// 本地状态
const [loading, setLoadingState] = useState(false);
const [selectedPrefs, setSelectedPrefs] = useState<string[]>([]);

// Redux状态
dispatch(setLoading(true));
dispatch(setRequirement(requirementData));
```

### 表单验证规则

```typescript
// 城市名称
{ required: true, message: '请输入目的地城市' }
{ min: 2, message: '城市名称至少2个字符' }

// 旅行天数
{ required: true, message: '请输入旅行天数' }
{ type: 'number', min: 1, max: 30, message: '天数范围为1-30天' }

// 出行人数
{ required: true, message: '请输入出行人数' }
{ type: 'number', min: 1, max: 20, message: '人数范围为1-20人' }

// 总预算
{ required: true, message: '请输入总预算' }
{ type: 'number', min: 1000, message: '最低预算1000元' }

// 出发日期
{ required: true, message: '请选择出发日期' }
```

## 📊 数据流示例

### 示例1：北京3日游

```json
{
  "user_id": "user_1234567890",
  "requirement": {
    "city_name": "北京",
    "travel_days": 3,
    "total_budget": 5000,
    "travel_type": "family",
    "start_date": "2026-06-01",
    "preferences": ["历史古迹", "美食探索", "文化体验"]
  }
}
```

### 示例2：上海情侣周末游

```json
{
  "user_id": "user_1234567890",
  "requirement": {
    "city_name": "上海",
    "travel_days": 2,
    "total_budget": 3000,
    "travel_type": "couple",
    "start_date": "2026-05-25",
    "preferences": ["购物休闲", "美食探索", "夜生活"]
  }
}
```

## 🎯 后续优化建议

### 短期优化
1. **城市autocomplete** - 输入城市名时自动补全
2. **预算智能推荐** - 根据城市和天数推荐合理预算范围
3. **历史偏好记忆** - 记住用户上次选择的偏好
4. **表单草稿保存** - 自动保存未提交的表单内容

### 长期优化
1. **AI智能推荐** - 根据用户画像推荐目的地
2. **地图选点** - 在地图上选择目的地
3. **多人协作** - 支持多人共同编辑行程需求
4. **模板快速填充** - 提供常用旅行模板一键填充

## 🐛 常见问题

### Q1: 为什么有些字段是可选的？
A: 出行类型和特殊需求是可选的，系统会根据必填信息生成基础行程，可选信息用于优化推荐结果。

### Q2: 预算包含哪些费用？
A: 总预算应包含交通、住宿、餐饮、门票、购物等所有旅行相关费用。系统会自动按比例分配（住宿30%、餐饮25%、交通15%、门票20%、其他10%）。

### Q3: 可以选择多个偏好吗？
A: 是的，最多可以选择5个偏好标签，选择越多，生成的行程越符合您的兴趣。

### Q4: 提交后能否修改需求？
A: 提交后会生成唯一的requirement_id，如需修改，可以重新提交新的需求表单。

### Q5: 为什么不能选择过去的日期？
A: 系统只支持规划未来的行程，过去的日期无法生成有效的行程安排。

## 📱 响应式适配

| 设备 | 屏幕宽度 | 布局方式 |
|------|---------|---------|
| 手机竖屏 | < 576px | 单列布局 |
| 手机横屏 | ≥ 576px | 单列布局 |
| 平板竖屏 | ≥ 768px | 双列布局 |
| 平板横屏 | ≥ 992px | 三列布局 |
| 桌面显示器 | ≥ 1200px | 三列布局 |

## 🔗 相关API接口

### 提交需求
- **接口**: `POST /api/v1/requirement/submit`
- **请求体**: 
```json
{
  "user_id": "string",
  "requirement": {
    "city_name": "string",
    "travel_days": number,
    "total_budget": number,
    "travel_type": "string",
    "start_date": "YYYY-MM-DD",
    "preferences": ["string"]
  }
}
```
- **响应**:
```json
{
  "code": 200,
  "msg": "需求提交成功",
  "data": {
    "requirement_id": "uuid",
    "status": "pending"
  }
}
```

### 任务分解
- **接口**: `POST /api/v1/task/decompose`
- **请求体**:
```json
{
  "requirement_id": "uuid",
  "structured_requirement": {
    "city_name": "string",
    "travel_days": number,
    "total_budget": number,
    "travel_date": "YYYY-MM-DD",
    "traveler_count": number,
    "preferences": ["string"]
  }
}
```

---

**最后更新**: 2026-05-23  
**版本**: v1.0.0
