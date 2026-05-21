# agents/travel_planner.py - 新建：人性化旅行计划生成器

from typing import Dict, List, Any
from datetime import datetime


class TravelPlanGenerator:
    """
    旅行计划生成器
    将结构化的API数据转换为人性化的自然语言输出
    """
    
    @staticmethod
    def generate_human_readable_plan(task_results: Dict[str, Any], 
                                     user_request: str) -> str:
        """
        生成人性化的旅行计划
        
        参数：
            task_results: 各任务的执行结果
            user_request: 用户原始请求
        
        返回：自然语言风格的旅行计划
        """
        
        plan_parts = []
        
        # 开场白
        plan_parts.append(TravelPlanGenerator._generate_greeting(user_request))
        
        # 天气信息
        if "weather" in task_results:
            weather_text = TravelPlanGenerator._format_weather(task_results["weather"])
            if weather_text:
                plan_parts.append(weather_text)
        
        # 路线规划
        if "route" in task_results:
            route_text = TravelPlanGenerator._format_route(task_results["route"])
            if route_text:
                plan_parts.append(route_text)
        
        # 住宿推荐
        if "hotel" in task_results:
            hotel_text = TravelPlanGenerator._format_hotels(task_results["hotel"])
            if hotel_text:
                plan_parts.append(hotel_text)
        
        # 美食推荐
        if "food" in task_results:
            food_text = TravelPlanGenerator._format_food(task_results["food"])
            if food_text:
                plan_parts.append(food_text)
        
        # 结束语
        plan_parts.append(TravelPlanGenerator._generate_closing())
        
        return "\n\n".join(plan_parts)
    
    @staticmethod
    def _generate_greeting(user_request: str) -> str:
        """生成友好的开场白"""
        greetings = [
            f"您好！根据您的请求\"{user_request}\"，我为您精心准备了一份旅行计划：",
            f"很高兴为您服务！针对您的出行需求，我整理了以下建议：",
            f"收到您的旅行计划请求啦！让我来帮您规划一下："
        ]
        return greetings[0]
    
    @staticmethod
    def _format_weather(weather_data: Dict[str, Any]) -> str:
        """格式化天气信息"""
        if not weather_data or "error" in weather_data:
            return ""
        
        lines = ["🌤️ **天气情况**"]
        
        # 支持两种数据格式：嵌套格式(lives)和扁平格式(直接字段)
        if "lives" in weather_data:
            # 格式1: 嵌套结构（高德原始格式）
            live = weather_data["lives"][0]
            city = live.get("city", "当地")
            weather = live.get("weather", "未知")
            temp = live.get("temperature", "--")
            wind_dir = live.get("winddirection", "")
            wind_power = live.get("windpower", "")
            humidity = live.get("humidity", "")
            
            lines.append(f"   {city}现在的天气是{weather}，气温{temp}℃。")
            
            if wind_dir and wind_power:
                wind_desc = TravelPlanGenerator._describe_wind(wind_dir, wind_power)
                lines.append(f"   风向{wind_desc}，湿度{humidity}%。")
            
            # 给出建议
            advice = TravelPlanGenerator._get_weather_advice(weather, temp)
            if advice:
                lines.append(f"   💡 {advice}")
        
        elif "city" in weather_data:
            # 格式2: 扁平结构（AmapWeatherService返回的格式）
            city = weather_data.get("city", "当地")
            weather = weather_data.get("weather", "未知")
            temp = weather_data.get("temperature", "--")
            wind_dir = weather_data.get("wind_direction", "")
            wind_power = weather_data.get("wind_power", "")
            humidity = weather_data.get("humidity", "")
            
            lines.append(f"   {city}现在的天气是{weather}，气温{temp}℃。")
            
            if wind_dir and wind_power:
                wind_desc = TravelPlanGenerator._describe_wind(wind_dir, wind_power)
                lines.append(f"   风向{wind_desc}，湿度{humidity}%。")
            
            # 给出建议
            advice = TravelPlanGenerator._get_weather_advice(weather, temp)
            if advice:
                lines.append(f"   💡 {advice}")
        
        elif "casts" in weather_data:
            # 天气预报
            lines.append("   📅 **未来几天预报：**")
            casts = weather_data["casts"][:3]  # 显示前3天
            
            for cast in casts:
                date = cast.get("date", "")
                day_weather = cast.get("dayweather", "")
                night_weather = cast.get("nightweather", "")
                day_temp = cast.get("daytemp", "")
                night_temp = cast.get("nighttemp", "")
                
                lines.append(f"   • {date}: 白天{day_weather}({day_temp}℃) / 夜间{night_weather}({night_temp}℃)")
        
        return "\n".join(lines)
    
    @staticmethod
    def _format_route(route_data: Dict[str, Any]) -> str:
        """格式化路线信息"""
        if not route_data or "error" in route_data:
            return ""
        
        lines = ["🚗 **交通路线**"]
        
        origin = route_data.get("origin_name", "起点")
        destination = route_data.get("destination_name", "终点")
        distance = route_data.get("distance", 0)
        duration = route_data.get("duration", 0)
        route_type = route_data.get("route_type", "driving")
        
        # 转换单位
        if distance >= 1000:
            dist_str = f"{distance/1000:.1f}公里"
        else:
            dist_str = f"{distance}米"
        
        dur_min = duration / 60
        if dur_min >= 60:
            time_str = f"{dur_min/60:.1f}小时"
        else:
            time_str = f"{dur_min:.0f}分钟"
        
        # 路线类型描述
        type_desc = {
            "driving": "驾车",
            "walking": "步行",
            "transit": "公交"
        }.get(route_type, "出行")
        
        lines.append(f"   从{origin}到{destination}，{type_desc}大约需要{time_str}，路程{dist_str}。")
        
        # 详细步骤
        steps = route_data.get("steps", [])
        if steps:
            lines.append(f"\n   📍 **详细路线：**")
            for i, step in enumerate(steps[:5], 1):  # 最多显示5步
                instruction = step.get("instruction", "")
                step_dist = step.get("distance", "")
                
                if step_dist:
                    if int(step_dist) >= 1000:
                        step_dist_str = f"{int(step_dist)/1000:.1f}公里"
                    else:
                        step_dist_str = f"{step_dist}米"
                    lines.append(f"   {i}. {instruction}（{step_dist_str}）")
                else:
                    lines.append(f"   {i}. {instruction}")
            
            if len(steps) > 5:
                lines.append(f"   ... 还有{len(steps)-5}个步骤")
        
        # 公交特殊信息
        if route_type == "transit" and "cost" in route_data:
            cost = route_data.get("cost", "未知")
            lines.append(f"\n   💰 预计费用：{cost}元")
        
        return "\n".join(lines)
    
    @staticmethod
    def _format_hotels(hotel_data: Dict[str, Any]) -> str:
        """格式化酒店推荐"""
        if not hotel_data or "error" in hotel_data:
            return ""
        
        pois = hotel_data.get("pois", [])
        if not pois:
            return ""
        
        lines = ["🏨 **住宿推荐**"]
        lines.append(f"   为您找到{len(pois)}家不错的酒店：\n")
        
        for i, hotel in enumerate(pois[:3], 1):  # 最多显示3家
            name = hotel.get("name", "未知酒店")
            address = hotel.get("address", "")
            rating = hotel.get("rating", "暂无评分")
            
            lines.append(f"   {i}. **{name}**")
            if address:
                lines.append(f"      📍 {address}")
            if rating and rating != "暂无评分":
                lines.append(f"      ⭐ 评分: {rating}")
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def _format_food(food_data: Dict[str, Any]) -> str:
        """格式化美食推荐"""
        if not food_data or "error" in food_data:
            return ""
        
        pois = food_data.get("pois", [])
        if not pois:
            return ""
        
        lines = ["🍜 **美食推荐**"]
        lines.append(f"   附近有一些值得品尝的美食：\n")
        
        for i, restaurant in enumerate(pois[:4], 1):  # 最多显示4家
            name = restaurant.get("name", "未知餐厅")
            address = restaurant.get("address", "")
            
            lines.append(f"   {i}. {name}")
            if address:
                lines.append(f"      📍 {address}")
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def _generate_closing() -> str:
        """生成友好的结束语"""
        closings = [
            "希望这份计划对您有帮助！祝您旅途愉快！🎉",
            "以上就是我为您准备的旅行建议，有任何问题随时问我哦！😊",
            "祝您的旅行顺利愉快！如果需要调整计划，随时告诉我~ ✨"
        ]
        return closings[0]
    
    @staticmethod
    def _describe_wind(direction: str, power: str) -> str:
        """描述风力"""
        try:
            power_num = float(power)
            if power_num <= 2:
                return f"{direction}风微风"
            elif power_num <= 4:
                return f"{direction}风{power_num}级"
            else:
                return f"{direction}风较强({power_num}级)"
        except:
            return f"{direction}风"
    
    @staticmethod
    def _get_weather_advice(weather: str, temp: str) -> str:
        """根据天气给出建议"""
        advice_list = []
        
        try:
            temp_num = int(temp)
            
            if temp_num < 10:
                advice_list.append("天气较冷，注意保暖，建议穿厚外套")
            elif temp_num > 30:
                advice_list.append("天气炎热，注意防暑降温，多喝水")
            
            if "雨" in weather:
                advice_list.append("有降雨，记得带伞☔")
            elif "雪" in weather:
                advice_list.append("有降雪，路面可能湿滑，注意安全")
            elif "晴" in weather:
                advice_list.append("天气晴朗，适合户外活动☀️")
            
        except:
            pass
        
        return "；".join(advice_list) if advice_list else ""
    
    @staticmethod
    def generate_summary_for_api(task_results: Dict[str, Any], 
                                 negotiation_logs: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成供前端调用的结构化摘要
        
        返回：包含人性化文本和协商日志的JSON
        """
        return {
            "status": "success",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "human_readable_plan": TravelPlanGenerator.generate_human_readable_plan(
                task_results, 
                user_request="旅行规划"
            ),
            "negotiation_details": negotiation_logs,
            "raw_data": task_results
        }


# 测试
if __name__ == "__main__":
    generator = TravelPlanGenerator()
    
    # 模拟任务结果
    task_results = {
        "weather": {
            "lives": [{
                "city": "北京",
                "weather": "晴",
                "temperature": "25",
                "winddirection": "南",
                "windpower": "2",
                "humidity": "45"
            }]
        },
        "route": {
            "origin_name": "天安门",
            "destination_name": "故宫",
            "distance": 1500,
            "duration": 480,
            "route_type": "driving",
            "steps": [
                {"instruction": "向北行驶396米左转", "distance": "396"},
                {"instruction": "沿东华门路向西行驶80米", "distance": "80"}
            ]
        },
        "hotel": {
            "pois": [
                {"name": "北京饭店", "address": "东城区东长安街", "rating": "4.5"},
                {"name": "王府井酒店", "address": "王府井大街", "rating": "4.2"}
            ]
        }
    }
    
    plan = generator.generate_human_readable_plan(task_results, "我想去北京玩")
    print(plan)
