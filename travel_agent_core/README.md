# 多智能体旅游规划系统

基于合同网协议的多智能体协作核心，能够调用和风天气与高德地图 API，自动生成旅行计划。

## 快速开始

### 1. 克隆项目
git clone https://github.com/march-frogs/agent-core.git
cd agent-core

### 2. 安装依赖
pip install -r requirements.txt

### 3. 配置 API Key
cp .env.example .env
# 编辑 .env 文件，填入你的 QWEATHER_API_KEY 和 AMAP_API_KEY

### 4. 运行
python main.py

你将看到多个智能体协作，生成一份包含天气、酒店、美食和路线的北京三日游计划。