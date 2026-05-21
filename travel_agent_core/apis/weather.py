import os
import requests
import json
from typing import Dict, Optional, List
import pathlib
from dotenv import load_dotenv

# 高德地图天气 API 端点
AMAP_WEATHER_URL = "https://restapi.amap.com/v3/weather/weatherInfo"

# 自动加载 .env 文件 (兼容直接运行此脚本的情况)
dotenv_path = pathlib.Path(__file__).parent.parent / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)

class WeatherAPI:
    def __init__(self, api_key: Optional[str] = None):
        # 优先使用传入的 key，其次从环境变量获取
        self.api_key = api_key or os.getenv("AMAP_KEY")
        
        if not self.api_key:
            raise ValueError("未找到高德地图 API Key。请在 .env 文件中设置 AMAP_KEY，或在初始化时传入 api_key。")

        # 设置默认的请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/json"
        }

    def _fetch_amap_weather(self, location: str, extensions: str = "base") -> Dict:
        """
        内部方法：调用高德地图天气 API
        :param location: 城市名称或 Adcode
        :param extensions: base (实况) 或 all (预报)
        :return: 原始数据字典
        """
        params = {
            "city": location,
            "key": self.api_key,
            "extensions": extensions,
            "output": "JSON"
        }
        
        print(f"[DEBUG] 正在请求高德天气 API: {AMAP_WEATHER_URL}")
        print(f"[DEBUG] 请求参数: {params}")
        
        try:
            response = requests.get(AMAP_WEATHER_URL, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            print(f"[DEBUG] 高德 API 响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if data.get("status") == "1" and data.get("count") != "0":
                return data
            else:
                print(f"[ERROR] 高德 API 返回错误: {data.get('info')}")
                return {"error": f"高德 API 错误: {data.get('info')}"}
                
        except Exception as e:
            print(f"[ERROR] 请求高德 API 失败: {str(e)}")
            return {"error": f"请求失败: {str(e)}"}

    def get_current_weather(self, location: str) -> Dict:
        """
        获取实况天气 (使用高德地图)
        :param location: 城市名称
        :return: 天气数据字典
        """
        print(f"\n--- 测试实况天气 ---")
        print(f"[WeatherAPI] 正在查询 {location} 天气 (模式: now)...")
        
        data = self._fetch_amap_weather(location, extensions="base")
        
        if "error" in data:
            return data
            
        # 高德实况数据结构: lives[0]
        if data.get("lives"):
            live = data["lives"][0]
            # 格式化返回数据，保持与之前类似的键名以便上层兼容，或者直接使用高德字段
            return {
                "province": live.get("province"),
                "city": live.get("city"),
                "weather": live.get("weather"),
                "temperature": live.get("temperature"),
                "winddirection": live.get("winddirection"),
                "windpower": live.get("windpower"),
                "humidity": live.get("humidity"),
                "reporttime": live.get("reporttime")
            }
        else:
            return {"error": "未获取到实况天气数据"}

    def get_forecast_weather(self, location: str, days: int = 3) -> List[Dict]:
        """
        获取未来天气预报 (使用高德地图)
        注意：高德免费版通常提供 3-4 天预报
        :param location: 城市名称
        :param days: 预报天数 (高德通常返回3-4天)
        :return: 天气数据列表
        """
        print(f"\n--- 测试未来{days}天预报 ---")
        print(f"[WeatherAPI] 正在查询 {location} 天气 (模式: daily)...")
        
        data = self._fetch_amap_weather(location, extensions="all")
        
        if "error" in data:
            return [data]
            
        # 高德预报数据结构: forecasts[0].casts
        if data.get("forecasts"):
            forecast_list = data["forecasts"][0].get("casts", [])
            # 限制返回天数
            return forecast_list[:days]
        else:
            return [{"error": "未获取到预报天气数据"}]

if __name__ == "__main__":
    try:
        # 直接实例化，类内部会自动从环境变量读取 AMAP_KEY
        weather_api = WeatherAPI() 
        print("[INFO] 成功从环境变量加载 API Key")
    except ValueError as e:
        print(f"[ERROR] {e}")
        exit(1)
    
    # 测试用例
    city = "北京"
    
    # 1. 测试实况天气
    current_weather = weather_api.get_current_weather(city)
    print("实况天气结果:", json.dumps(current_weather, ensure_ascii=False, indent=2))
    
    # 2. 测试未来3天预报
    forecast_weather = weather_api.get_forecast_weather(city, days=3)
    print("预报天气结果:", json.dumps(forecast_weather, ensure_ascii=False, indent=2))