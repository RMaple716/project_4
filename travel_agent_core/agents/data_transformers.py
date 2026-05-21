"""
数据转换器模块
将各 API 返回的原始数据转换为符合规范的结构化格式
"""
import uuid
from typing import Dict, List, Any, Optional


class AttractionTransformer:
    """
    景点数据转换器
    将高德 POI 数据转换为规范的景点格式
    """
    
    @staticmethod
    def transform(poi: Dict, preferences: Optional[List[str]] = None, dislikes: Optional[List[str]] = None) -> Dict:
        """
        转换单个景点数据
        
        Args:
            poi: 高德 POI 原始数据
            preferences: 用户偏好标签
            dislikes: 用户排除标签
            
        Returns:
            规范化的景点数据
        """
        # 解析坐标（高德格式：lng,lat）
        location_str = poi.get("location", "")
        lat, lng = None, None
        if location_str and "," in location_str:
            try:
                parts = location_str.split(",")
                lng = float(parts[0])
                lat = float(parts[1])
            except (ValueError, IndexError):
                pass
        
        # 提取标签
        tags = AttractionTransformer._extract_tags(poi, preferences, dislikes)
        
        # 建议游览时段
        time_slot = AttractionTransformer._suggest_time_slot(poi)
        
        return {
            "id": f"att_{uuid.uuid4().hex[:8]}",  # 带前缀的唯一ID
            "name": poi.get("name", "未知景点"),
            "category": poi.get("type", "其他"),
            "suggested_duration": AttractionTransformer._estimate_duration(poi),
            "visit_time_slot": time_slot,  # morning/afternoon/evening
            "ticket_price": 0,  # 高德无票价信息，需额外API
            "location": {
                "lat": lat,
                "lng": lng
            } if lat and lng else {"lat": None, "lng": None},
            "tags": tags,
            "address": poi.get("address", ""),
            "rating": float(poi.get("biz_ext", {}).get("rating", 0)) if poi.get("biz_ext") else 0
        }
    
    @staticmethod
    def transform_list(pois: List[Dict], preferences: Optional[List[str]] = None, 
                      dislikes: Optional[List[str]] = None, max_count: int = 5) -> List[Dict]:
        """批量转换景点数据"""
        transformed = []
        for poi in pois[:max_count]:
            try:
                item = AttractionTransformer.transform(poi, preferences, dislikes)
                transformed.append(item)
            except Exception as e:
                print(f"[AttractionTransformer] 转换失败: {e}")
        return transformed
    
    @staticmethod
    def _extract_tags(poi: Dict, preferences: Optional[List[str]] = None, 
                     dislikes: Optional[List[str]] = None) -> List[str]:
        """提取景点标签"""
        tags = []
        poi_type = poi.get("type", "")
        
        # 根据类型添加标签
        if "公园" in poi_type or "景区" in poi_type:
            tags.append("户外")
        if "博物馆" in poi_type or "纪念馆" in poi_type:
            tags.append("室内")
        if "购物" in poi_type:
            tags.append("购物")
        
        # 添加用户偏好标签
        if preferences:
            for pref in preferences:
                if pref in poi_type or pref in poi.get("name", ""):
                    tags.append(pref)
        
        # 去重
        return list(set(tags))
    
    @staticmethod
    def _suggest_time_slot(poi: Dict) -> str:
        """根据景点类型建议游览时段"""
        poi_type = poi.get("type", "").lower()
        name = poi.get("name", "").lower()
        
        # 自然景观适合上午
        if any(kw in poi_type for kw in ["公园", "自然", "山", "湖"]):
            return "morning"
        
        # 博物馆/室内景点适合下午
        if any(kw in poi_type for kw in ["博物馆", "纪念馆", "展览馆", "室内"]):
            return "afternoon"
        
        # 夜景/餐饮街适合晚上
        if any(kw in poi_type for kw in ["夜市", "步行街", "酒吧"]):
            return "evening"
        
        # 默认上午
        return "morning"
    
    @staticmethod
    def _estimate_duration(poi: Dict) -> str:
        """估算游览时长"""
        poi_type = poi.get("type", "")
        
        if "博物馆" in poi_type:
            return "2-3小时"
        elif "公园" in poi_type or "景区" in poi_type:
            return "3-4小时"
        elif "购物" in poi_type:
            return "1-2小时"
        else:
            return "1-2小时"


class HotelTransformer:
    """
    住宿数据转换器
    将高德 POI 数据转换为规范的酒店格式
    """
    
    @staticmethod
    def transform(poi: Dict, budget_per_night: Optional[float] = None) -> Dict:
        """转换单个酒店数据"""
        # 解析坐标
        location_str = poi.get("location", "")
        lat, lng = None, None
        if location_str and "," in location_str:
            try:
                parts = location_str.split(",")
                lng = float(parts[0])
                lat = float(parts[1])
            except (ValueError, IndexError):
                pass
        
        # 估算价格（高德无真实价格，根据评分估算）
        rating = float(poi.get("biz_ext", {}).get("rating", 3.0)) if poi.get("biz_ext") else 3.0
        estimated_price = rating * 100  # 简单估算
        
        return {
            "id": f"hotel_{uuid.uuid4().hex[:8]}",  # 带前缀的唯一ID
            "name": poi.get("name", "未知酒店"),
            "address": poi.get("address", ""),
            "price_per_night": round(estimated_price, 2),
            "rating": rating,
            "distance_to_center_km": 0,  # 需要额外计算
            "amenities": ["WiFi"],  # 高德无此信息
            "location": {
                "lat": lat,
                "lng": lng
            } if lat and lng else {"lat": None, "lng": None}
        }
    
    @staticmethod
    def transform_list(pois: List[Dict], budget_per_night: Optional[float] = None, 
                      max_count: int = 3) -> tuple:
        """批量转换酒店数据，并按预算过滤"""
        transformed = []
        over_budget_count = 0
        
        for poi in pois:
            try:
                hotel = HotelTransformer.transform(poi, budget_per_night)
                
                # 预算过滤
                if budget_per_night and hotel["price_per_night"] > budget_per_night:
                    over_budget_count += 1
                    continue
                
                transformed.append(hotel)
                
                if len(transformed) >= max_count:
                    break
            except Exception as e:
                print(f"[HotelTransformer] 转换失败: {e}")
        
        return transformed, over_budget_count


class FoodTransformer:
    """
    美食数据转换器
    将高德 POI 数据转换为规范的餐厅格式
    """
    
    @staticmethod
    def transform(poi: Dict, budget_per_person: Optional[float] = None) -> Dict:
        """转换单个餐厅数据"""
        # 解析坐标
        location_str = poi.get("location", "")
        lat, lng = None, None
        if location_str and "," in location_str:
            try:
                parts = location_str.split(",")
                lng = float(parts[0])
                lat = float(parts[1])
            except (ValueError, IndexError):
                pass
        
        # 估算人均价格
        rating = float(poi.get("biz_ext", {}).get("rating", 3.5)) if poi.get("biz_ext") else 3.5
        estimated_price = rating * 20  # 简单估算
        
        return {
            "id": f"food_{uuid.uuid4().hex[:8]}",  # 带前缀的唯一ID
            "name": poi.get("name", "未知餐厅"),
            "cuisine": poi.get("type", "本地菜"),
            "avg_price_per_person": round(estimated_price, 2),
            "rating": rating,
            "recommended_dishes": [],  # 高德无此信息
            "location": {
                "lat": lat,
                "lng": lng
            } if lat and lng else {"lat": None, "lng": None},
            "address": poi.get("address", "")
        }
    
    @staticmethod
    def transform_list(pois: List[Dict], budget_per_person: Optional[float] = None, 
                      meal_type: str = "lunch", max_count: int = 4) -> tuple:
        """批量转换餐厅数据，并按预算过滤"""
        transformed = []
        over_budget_count = 0
        
        for poi in pois:
            try:
                restaurant = FoodTransformer.transform(poi, budget_per_person)
                
                # 预算过滤
                if budget_per_person and restaurant["avg_price_per_person"] > budget_per_person:
                    over_budget_count += 1
                    continue
                
                transformed.append(restaurant)
                
                if len(transformed) >= max_count:
                    break
            except Exception as e:
                print(f"[FoodTransformer] 转换失败: {e}")
        
        return transformed, over_budget_count


class TransportTransformer:
    """
    交通数据转换器
    将高德路线数据转换为规范的交通格式
    """
    
    @staticmethod
    def transform_route(route_data: Dict, origin_name: str = "", 
                       destination_name: str = "") -> Dict:
        """转换路线数据"""
        distance = route_data.get("distance", 0)
        duration = route_data.get("duration", 0)
        
        # 转换步骤
        steps = []
        if "steps" in route_data:
            for step in route_data.get("steps", [])[:5]:  # 最多5步
                steps.append({
                    "instruction": step.get("instruction", ""),
                    "distance_m": int(step.get("distance", 0))
                })
        
        return {
            "from": origin_name or "起点",
            "to": destination_name or "终点",
            "mode": route_data.get("route_type", "driving"),
            "duration_minutes": round(duration / 60, 1),
            "cost": route_data.get("cost", 0),
            "distance_m": distance,
            "steps": steps
        }
