import os
import requests
import json
from typing import Dict, Optional, List
import pathlib
from dotenv import load_dotenv

# 自动加载 .env 文件
dotenv_path = pathlib.Path(__file__).parent.parent / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)


class AmapService:
    """
    高德地图 POI 搜索服务
    提供地点搜索、详情查询等功能
    """
    
    # 高德地图 POI 搜索 API 端点
    POI_SEARCH_URL = "https://restapi.amap.com/v3/place/text"
    POI_DETAIL_URL = "https://restapi.amap.com/v3/place/detail"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("AMAP_KEY")
        
        if not self.api_key:
            raise ValueError("未找到高德地图 API Key。请在 .env 文件中设置 AMAP_KEY。")
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def search_poi(self, keywords: str, city: str, types: str = "", 
                   sortrule: str = "weight", offset: int = 20, page: int = 1, **kwargs) -> Dict:
        """
        POI 关键词搜索
        
        Args:
            keywords: 搜索关键词（如"美食"、"酒店"、"旅游景点"）
            city: 城市名称或 adcode
            types: POI 类型编码（可选，如"050000"表示餐饮）
            sortrule: 排序规则（weight:权重优先, distance:距离优先, price:价格优先）
            offset: 每页记录数（默认20，最大25）
            page: 页码（默认1）
            
        Returns:
            包含 pois 列表的字典
        """
        params = {
            "key": self.api_key,
            "keywords": keywords,
            "city": city,
            "sortrule": sortrule,
            "offset": offset,
            "page": page,
            "output": "JSON"
        }
        
        # 如果指定了类型，添加到参数中
        if types:
            params["types"] = types
        
        print(f"[AmapService] 正在搜索 POI: {keywords} in {city}")
        print(f"[DEBUG] 请求参数: {params}")
        
        try:
            response = requests.get(self.POI_SEARCH_URL, params=params, 
                                  headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            print(f"[DEBUG] 高德 POI API 响应状态: {data.get('status')}")
            
            if data.get("status") == "1" and int(data.get("count", 0)) > 0:
                pois = data.get("pois", [])
                
                # 格式化返回数据，提取关键信息
                formatted_pois = []
                for poi in pois[:10]:  # 最多返回10条结果
                    formatted_poi = {
                        "id": poi.get("id"),
                        "name": poi.get("name"),
                        "type": poi.get("type"),
                        "address": poi.get("address"),
                        "location": poi.get("location"),  # 经纬度 "lng,lat"
                        "tel": poi.get("tel"),
                        "biz_ext": {
                            "rating": poi.get("biz_ext", {}).get("rating", 0),
                            "cost": poi.get("biz_ext", {}).get("cost", 0),
                            "ticket_ordering": poi.get("biz_ext", {}).get("ticket_ordering", "")
                        },
                        "photos": poi.get("photos", [])[:3] if poi.get("photos") else []
                    }
                    formatted_pois.append(formatted_poi)
                
                result = {
                    "pois": formatted_pois,
                    "total_count": int(data.get("count", 0)),
                    "suggestion": data.get("suggestion", {})
                }
                
                print(f"[AmapService] 成功获取 {len(formatted_pois)} 条 POI 数据")
                return result
            else:
                print(f"[WARNING] 高德 POI API 未返回有效数据: {data.get('info')}")
                return {"pois": [], "total_count": 0, "error": data.get("info")}
                
        except Exception as e:
            print(f"[ERROR] 请求高德 POI API 失败: {str(e)}")
            return {"pois": [], "total_count": 0, "error": f"请求失败: {str(e)}"}
    
    def get_poi_detail(self, poi_id: str, **kwargs) -> Dict:
        """
        获取 POI 详细信息
        
        Args:
            poi_id: POI ID
            
        Returns:
            POI 详细信息字典
        """
        params = {
            "key": self.api_key,
            "id": poi_id,
            "output": "JSON"
        }
        
        try:
            response = requests.get(self.POI_DETAIL_URL, params=params,
                                  headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "1" and data.get("pois"):
                return data["pois"][0]
            else:
                return {"error": data.get("info")}
                
        except Exception as e:
            print(f"[ERROR] 获取 POI 详情失败: {str(e)}")
            return {"error": f"请求失败: {str(e)}"}


class AmapRouteService:
    """
    高德地图路线规划服务
    提供驾车、步行、公交等路线规划
    """
    
    # 高德地图路线规划 API 端点
    DRIVING_ROUTE_URL = "https://restapi.amap.com/v3/direction/driving"
    WALKING_ROUTE_URL = "https://restapi.amap.com/v3/direction/walking"
    TRANSIT_ROUTE_URL = "https://restapi.amap.com/v3/direction/transit/integrated"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("AMAP_KEY")
        
        if not self.api_key:
            raise ValueError("未找到高德地图 API Key。请在 .env 文件中设置 AMAP_KEY。")
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def get_route(self, origin: str, destination: str, city: str = "",
                  strategy: int = 0, extensions: str = "base", **kwargs) -> Dict:
        """
        驾车路线规划
        
        Args:
            origin: 起点坐标（格式：经度,纬度 或 地址文本）
            destination: 终点坐标（格式：经度,纬度 或 地址文本）
            city: 城市名称（用于地址解析）
            strategy: 路线策略
                     0: 速度优先
                     1: 费用优先
                     2: 距离优先
                     3: 不走高速
            extensions: 返回结果详细程度（base:基本，all:详细）
            
        Returns:
            路线规划结果字典
        """
        params = {
            "key": self.api_key,
            "origin": origin,
            "destination": destination,
            "strategy": strategy,
            "extensions": extensions,
            "output": "JSON"
        }
        
        if city:
            params["city"] = city
        
        print(f"[AmapRouteService] 正在规划路线: {origin} -> {destination}")
        print(f"[DEBUG] 请求参数: {params}")
        
        try:
            response = requests.get(self.DRIVING_ROUTE_URL, params=params,
                                  headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            print(f"[DEBUG] 高德路线 API 响应状态: {data.get('status')}")
            
            if data.get("status") == "1" and data.get("route"):
                route = data["route"]
                paths = route.get("paths", [])
                
                if paths:
                    # 取第一条路线
                    path = paths[0]
                    
                    result = {
                        "distance": int(path.get("distance", 0)),  # 米
                        "duration": int(path.get("duration", 0)),  # 秒
                        "tolls": float(path.get("tolls", 0)),      # 过路费
                        "steps": []
                    }
                    
                    # 提取路线步骤
                    for step in path.get("steps", [])[:10]:  # 最多10个步骤
                        result["steps"].append({
                            "instruction": step.get("instruction"),
                            "action": step.get("action"),
                            "distance": step.get("distance"),
                            "road": step.get("road")
                        })
                    
                    print(f"[AmapRouteService] 路线规划成功: {result['distance']}米, {result['duration']}秒")
                    return result
                else:
                    return {"error": "未找到可行路线"}
            else:
                print(f"[WARNING] 高德路线 API 未返回有效数据: {data.get('info')}")
                return {"error": data.get("info")}
                
        except Exception as e:
            print(f"[ERROR] 请求高德路线 API 失败: {str(e)}")
            return {"error": f"请求失败: {str(e)}"}
    
    def get_walking_route(self, origin: str, destination: str, **kwargs) -> Dict:
        """
        步行路线规划
        
        Args:
            origin: 起点坐标
            destination: 终点坐标
            
        Returns:
            步行路线结果
        """
        params = {
            "key": self.api_key,
            "origin": origin,
            "destination": destination,
            "output": "JSON"
        }
        
        try:
            response = requests.get(self.WALKING_ROUTE_URL, params=params,
                                  headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "1" and data.get("route"):
                path = data["route"]["paths"][0] if data["route"].get("paths") else {}
                
                return {
                    "distance": int(path.get("distance", 0)),
                    "duration": int(path.get("duration", 0)),
                    "steps": path.get("steps", [])[:5]
                }
            else:
                return {"error": data.get("info")}
                
        except Exception as e:
            print(f"[ERROR] 步行路线规划失败: {str(e)}")
            return {"error": f"请求失败: {str(e)}"}


# 为了向后兼容，提供别名
AmapAPI = AmapService
