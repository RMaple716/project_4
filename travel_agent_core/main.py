import os
from dotenv import load_dotenv
import pathlib
import asyncio
from typing import Optional
from core.bus import MessageBus
from core.message import Message
from agents.orchestrator import OrchestratorAgent
from agents.worker import WorkerAgent
from agents.base import BaseAgent
from apis.weather import WeatherAPI
from apis.amap import AmapService, AmapRouteService

# 加载 .env 文件中的环境变量
dotenv_path = pathlib.Path(__file__).parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

class UserAgent(BaseAgent):
    """模拟用户，发起请求并接收最终计划"""
    def __init__(self, agent_id="user"):
        super().__init__(agent_id)
        # 覆盖父类的 mailbox，使用自己的 Queue
        self.mailbox = asyncio.Queue()

    async def handle_message(self, msg: Message):
        """处理接收到的消息（实现抽象方法）"""
        if msg.type == "final_plan":
            print("\n" + "="*50)
            print("📋 为您生成的旅行计划：")
            print(msg.content)
            print("="*50)
        elif msg.type == "error":
            print(f"\n❌ 收到错误消息: {msg.content}")
        else:
            print(f"[User] 收到中间消息 [{msg.type}]: {str(msg.content)[:100]}...")

    async def send_request(self, text: str, recipient: str):
        msg = Message(
            type="user_request",
            sender=self.agent_id,
            recipient=recipient,
            content=text
        )
        assert self.bus is not None
        await self.bus.route_message(msg)
        

    async def run_until_plan(self):
        """持续监听，直到收到最终计划"""
        while True:
            msg = await self.mailbox.get()
            if msg.type == "final_plan":
                return msg.content
            elif msg.type == "error":
                raise Exception(f"收到错误消息: {msg.content}")
            
            self.mailbox.task_done()


async def main():
    # 1. 创建核心组件
    bus = MessageBus()

    # 2. 创建 API 实例并检查初始化
    weather_api = None
    
    try:
        # WeatherAPI 现在内部会自动读取 AMAP_KEY 环境变量
        weather_api = WeatherAPI()
        print("[DEBUG] WeatherAPI 实例创建成功")
        
        # [新增] 直接测试高德地图天气 API 连通性
        if weather_api:
            print("[TEST] 正在测试高德天气 API 连通性 (获取未来3天预报)...")
            try:
                test_result = weather_api.get_forecast_weather("北京", days=3)
                print(f"[TEST] 高德天气 API 响应预览: {str(test_result)[:200]}...")
                
                # 统一处理返回值
                if isinstance(test_result, list):
                    if len(test_result) > 0:
                        first_item = test_result[0]
                        if isinstance(first_item, dict) and 'error' in first_item:
                            print(f"[ERROR] 高德天气 API 返回错误: {first_item['error']}")
                        else:
                            print("[SUCCESS] 高德天气 API 连接正常，已成功获取数据。")
                    else:
                        print("[WARNING] 高德天气 API 返回空列表。")
                elif isinstance(test_result, dict):
                    if 'error' in test_result:
                         print(f"[ERROR] 高德天气 API 返回错误: {test_result['error']}")
                    else:
                        print("[SUCCESS] 高德天气 API 连接正常，已成功获取数据。")
                        
            except Exception as e:
                print(f"[ERROR] 高德天气 API 测试调用异常: {e}")
                import traceback
                traceback.print_exc()
    except Exception as e:
        print(f"[ERROR] WeatherAPI 初始化失败: {e}")
        weather_api = None

    # 如果关键 API 都不可用，提前退出
    if not weather_api:
        print("[CRITICAL] 天气 API 初始化失败，无法生成有效计划。请检查 API Key 和网络连接。")
        return

    # 3. 创建智能体（使用真实的 API 服务）
    orchestrator = OrchestratorAgent("orchestrator")
    
    # 创建天气 Worker（使用真实的 WeatherAPI）
    weather_bot = WorkerAgent("weather_bot", ["get_forecast_weather"], weather_api)
    
    # 创建高德地图 POI 搜索服务
    try:
        amap_service = AmapService()
        print("[DEBUG] AmapService 实例创建成功")
        
        # 测试 POI 搜索连通性
        print("[TEST] 正在测试高德 POI 搜索 API...")
        test_result = amap_service.search_poi(keywords="旅游景点", city="北京", offset=5)
        if test_result.get("pois"):
            print(f"[SUCCESS] 高德 POI API 连接正常，找到 {len(test_result['pois'])} 个地点")
        else:
            print(f"[WARNING] 高德 POI API 返回空结果: {test_result.get('error')}")
    except Exception as e:
        print(f"[ERROR] AmapService 初始化失败: {e}")
        amap_service = None
    
    # 创建高德地图路线规划服务
    try:
        route_service = AmapRouteService()
        print("[DEBUG] AmapRouteService 实例创建成功")
        
        # 测试路线规划连通性
        print("[TEST] 正在测试高德路线规划 API...")
        test_result = route_service.get_route(
            origin="北京市中心",
            destination="故宫博物院",
            city="北京"
        )
        if "distance" in test_result:
            print(f"[SUCCESS] 高德路线 API 连接正常，距离 {test_result['distance']}米")
        else:
            print(f"[WARNING] 高德路线 API 返回错误: {test_result.get('error')}")
    except Exception as e:
        print(f"[ERROR] AmapRouteService 初始化失败: {e}")
        route_service = None
    
    # 创建其他 Workers（使用真实 API 服务）
    poi_bot = None
    route_bot = None
    
    if amap_service:
        poi_bot = WorkerAgent("poi_bot", ["search_poi"], amap_service)
    
    if route_service:
        route_bot = WorkerAgent("route_bot", ["get_route"], route_service)
    
    # 检查是否有可用的 Worker
    active_workers = [w for w in [weather_bot, poi_bot, route_bot] if w is not None]
    if not active_workers:
        print("[CRITICAL] 所有外部 API 均初始化失败，无法生成有效计划。请检查 API Key 和网络连接。")
        return
    
    print(f"\n[INFO] 已激活 {len(active_workers)} 个 Worker 智能体:")
    for worker in active_workers:
        print(f"  - {worker.agent_id}: {worker.capabilities}")

    # 4. 注册智能体到总线
    bus.register_agent(orchestrator)
    bus.register_agent(weather_bot)
    
    if poi_bot:
        bus.register_agent(poi_bot)
    
    if route_bot:
        bus.register_agent(route_bot)
    
    user = UserAgent("user")
    
    # ✅ 为所有智能体设置消息总线（必须在启动前调用）
    orchestrator.set_bus(bus)
    weather_bot.set_bus(bus)
    
    if poi_bot:
        poi_bot.set_bus(bus)
    
    if route_bot:
        route_bot.set_bus(bus)
    
    user.set_bus(bus)
    
    bus.register_agent(user)

    # 5. 订阅主题（如果需要广播机制）
    # bus.subscribe(agent_id, topic)

    # 6. 启动所有智能体
    await orchestrator.start()
    await weather_bot.start()
    
    if poi_bot:
        await poi_bot.start()
    
    if route_bot:
        await route_bot.start()
    
    await user.start()

    # 7. 用户发起请求
    print("\n" + "="*50)
    print("🚀 开始多智能体协作演示")
    print("="*50)
    
    request_text = "我想去北京玩3天，对历史古迹和美食感兴趣"
    print(f"\n📝 用户需求: {request_text}\n")
    
    await user.send_request(request_text, "orchestrator")

    # 8. 等待最终计划
    plan = await user.run_until_plan()

    # 9. 优雅停止
    await orchestrator.stop()
    await weather_bot.stop()
    
    if poi_bot:
        await poi_bot.stop()
    
    if route_bot:
        await route_bot.stop()
    
    await user.stop()

    return plan


if __name__ == "__main__":
    asyncio.run(main())