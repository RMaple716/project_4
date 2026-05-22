"""
协调层整体测试与Bug修复验证脚本

测试场景:
1. 时间冲突检测与修复验证
2. 多智能体通信数据格式验证
3. 行程整合边界情况处理
4. 预算校验功能测试
5. 路线优化算法验证
6. 异常数据处理
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:9091"


def test_time_conflict_detection():
    """测试1: 时间冲突检测功能"""
    print("\n=== 测试1: 时间冲突检测 ===")
    
    # 构造有明显时间冲突的行程
    schedule_with_conflict = [
        {
            "name": "故宫博物院",
            "start_time": "09:00",
            "end_time": "12:00",
            "activity_type": "attraction",
            "location": "北京市东城区"
        },
        {
            "name": "午餐",
            "start_time": "11:30",
            "duration": "1小时",
            "activity_type": "meal",
            "location": "王府井"
        }
    ]
    
    url = f"{BASE_URL}/api/v1/validation/time-conflict"
    payload = {"schedule": schedule_with_conflict}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get('code') == 200:
            data = result.get('data', {})
            has_conflict = data.get('has_conflict', False)
            conflicts = data.get('conflicts', [])
            
            print(f"✓ 检测到时间冲突: {has_conflict}")
            print(f"  冲突数量: {len(conflicts)}")
            
            if has_conflict and len(conflicts) > 0:
                print("  冲突详情:")
                for conflict in conflicts:
                    print(f"    - {conflict['description']} (严重程度: {conflict['severity']})")
                return True
            else:
                print("  ✗ 应该检测到冲突但未检测到")
                return False
        else:
            print(f"✗ 请求失败: {result.get('msg')}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        return False


def test_no_time_conflict():
    """测试2: 无时间冲突的正常行程"""
    print("\n=== 测试2: 无时间冲突的正常行程 ===")
    
    schedule_without_conflict = [
        {
            "name": "故宫博物院",
            "start_time": "09:00",
            "end_time": "11:30",
            "activity_type": "attraction",
            "location": "北京市东城区"
        },
        {
            "name": "午餐",
            "start_time": "12:00",
            "duration": "1小时",
            "activity_type": "meal",
            "location": "王府井"
        },
        {
            "name": "颐和园",
            "start_time": "14:00",
            "end_time": "16:30",
            "activity_type": "attraction",
            "location": "海淀区"
        }
    ]
    
    url = f"{BASE_URL}/api/v1/validation/time-conflict"
    payload = {"schedule": schedule_without_conflict}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get('code') == 200:
            data = result.get('data', {})
            has_conflict = data.get('has_conflict', False)
            
            if not has_conflict:
                print("✓ 正确识别为无冲突行程")
                return True
            else:
                print("✗ 错误地报告了冲突")
                conflicts = data.get('conflicts', [])
                for conflict in conflicts:
                    print(f"  - {conflict['description']}")
                return False
        else:
            print(f"✗ 请求失败: {result.get('msg')}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        return False


def test_budget_validation():
    """测试3: 预算校验功能"""
    print("\n=== 测试3: 预算校验 ===")
    
    agent_results = {
        "attraction": {
            "attractions": [
                {"name": "故宫", "ticket_price": 60, "visit_time_slot": "morning"},
                {"name": "颐和园", "ticket_price": 30, "visit_time_slot": "afternoon"}
            ]
        },
        "accommodation": {
            "hotels": [
                {"name": "北京酒店", "price_per_night": 800}
            ]
        },
        "food": {
            "restaurants": [
                {"name": "餐厅A", "avg_price_per_person": 150},
                {"name": "餐厅B", "avg_price_per_person": 200}
            ]
        },
        "transport": {
            "transport_options": []
        }
    }
    
    # 设置较低的预算，应该会超出
    structured_requirement = {
        "city_name": "北京",
        "travel_days": 1,
        "total_budget": 500,  # 很低的预算
        "travel_date": "2026-05-20",
        "traveler_count": 1
    }
    
    url = f"{BASE_URL}/api/v1/integration/combine"
    payload = {
        "task_id": "test_budget",
        "agent_results": agent_results,
        "structured_requirement": structured_requirement
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get('code') == 200:
            data = result.get('data', {})
            validation = data.get('validation', {})
            total_cost = data.get('total_cost', 0)
            
            print(f"  总花费: {total_cost} 元")
            print(f"  预算限制: {structured_requirement['total_budget']} 元")
            
            # 检查是否有预算超出的冲突
            conflicts = validation.get('conflicts', [])
            budget_conflict = any(c.get('type') == 'budget_exceeded' for c in conflicts)
            
            if budget_conflict:
                print("✓ 正确检测到预算超出")
                for c in conflicts:
                    if c.get('type') == 'budget_exceeded':
                        print(f"  冲突信息: {c['description']}")
                return True
            else:
                print("✗ 未检测到预算超出（可能计算有误）")
                return False
        else:
            print(f"✗ 请求失败: {result.get('msg')}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        return False


def test_empty_data_handling():
    """测试4: 空数据处理"""
    print("\n=== 测试4: 空数据处理 ===")
    
    agent_results_empty = {
        "attraction": {"attractions": []},
        "accommodation": {"hotels": []},
        "food": {"restaurants": []},
        "transport": {"transport_options": []}
    }
    
    structured_requirement = {
        "city_name": "北京",
        "travel_days": 1,
        "travel_date": "2026-05-20",
        "traveler_count": 1
    }
    
    url = f"{BASE_URL}/api/v1/integration/combine"
    payload = {
        "task_id": "test_empty",
        "agent_results": agent_results_empty,
        "structured_requirement": structured_requirement
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get('code') == 200:
            data = result.get('data', {})
            day_plans = data.get('day_plans', [])
            
            if len(day_plans) > 0:
                print("✓ 正确处理空数据，生成了行程框架")
                print(f"  生成天数: {len(day_plans)}")
                
                # 检查第一天是否为空活动
                day1 = day_plans[0]
                attractions_count = len(day1.get('attractions', []))
                meals_count = len(day1.get('meals', []))
                
                print(f"  景点数: {attractions_count}, 餐饮数: {meals_count}")
                return True
            else:
                print("✗ 未生成任何行程")
                return False
        else:
            print(f"✗ 请求失败: {result.get('msg')}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        return False


def test_multi_day_distribution():
    """测试5: 多天行程分配"""
    print("\n=== 测试5: 多天行程分配 ===")
    
    # 创建多个景点，测试是否能均匀分配到多天
    attractions = []
    time_slots = ["morning", "afternoon", "evening"]
    for i in range(9):  # 9个景点，3天，每天应该3个
        slot = time_slots[i % 3]
        attractions.append({
            "id": f"att_{i+1:03d}",
            "name": f"景点{i+1}",
            "visit_time_slot": slot,
            "ticket_price": 50,
            "location": {"lat": 39.9 + i * 0.01, "lng": 116.4}
        })
    
    agent_results = {
        "attraction": {"attractions": attractions},
        "accommodation": {
            "hotels": [{"name": "酒店", "price_per_night": 500}]
        },
        "food": {
            "restaurants": [
                {"name": "餐厅", "avg_price_per_person": 100}
            ]
        },
        "transport": {"transport_options": []}
    }
    
    structured_requirement = {
        "city_name": "北京",
        "travel_days": 3,
        "travel_date": "2026-05-20",
        "traveler_count": 1
    }
    
    url = f"{BASE_URL}/api/v1/integration/combine"
    payload = {
        "task_id": "test_multiday",
        "agent_results": agent_results,
        "structured_requirement": structured_requirement
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get('code') == 200:
            data = result.get('data', {})
            day_plans = data.get('day_plans', [])
            
            print(f"✓ 生成了 {len(day_plans)} 天的行程")
            
            # 检查每天的景点分配
            for day_plan in day_plans:
                day_num = day_plan.get('day')
                attractions_count = len(day_plan.get('attractions', []))
                print(f"  第{day_num}天: {attractions_count} 个景点")
            
            # 理想情况下，9个景点应该均匀分配到3天
            total_attractions = sum(len(dp.get('attractions', [])) for dp in day_plans)
            print(f"  总景点数: {total_attractions}")
            
            if total_attractions == 9:
                print("✓ 所有景点都被分配到行程中")
                return True
            else:
                print(f"✗ 景点分配不完整（期望9个，实际{total_attractions}个）")
                return False
        else:
            print(f"✗ 请求失败: {result.get('msg')}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        return False


def test_route_optimization_quality():
    """测试6: 路线优化质量"""
    print("\n=== 测试6: 路线优化质量 ===")
    
    # 创建地理位置分散的景点
    attractions = [
        {"name": "景点A-南", "location": {"lat": 39.8, "lng": 116.4}},
        {"name": "景点B-北", "location": {"lat": 40.1, "lng": 116.4}},
        {"name": "景点C-中", "location": {"lat": 39.95, "lng": 116.4}},
        {"name": "景点D-南", "location": {"lat": 39.82, "lng": 116.4}},
        {"name": "景点E-北", "location": {"lat": 40.08, "lng": 116.4}}
    ]
    
    url = f"{BASE_URL}/api/v1/integration/optimize-route"
    payload = {"attractions": attractions}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get('code') == 200:
            optimized = result.get('data', {}).get('optimized_attractions', [])
            
            print("✓ 路线优化成功")
            print("  优化后顺序:")
            for i, attr in enumerate(optimized, 1):
                lat = attr['location']['lat']
                print(f"    {i}. {attr['name']} (纬度: {lat:.2f})")
            
            # 检查是否按纬度排序（从南到北或从北到南）
            lats = [attr['location']['lat'] for attr in optimized]
            is_sorted = all(lats[i] <= lats[i+1] for i in range(len(lats)-1)) or \
                       all(lats[i] >= lats[i+1] for i in range(len(lats)-1))
            
            if is_sorted:
                print("✓ 路线已按地理位置排序")
                return True
            else:
                print("✗ 路线未按地理位置排序")
                return False
        else:
            print(f"✗ 请求失败: {result.get('msg')}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        return False


def test_itinerary_validation_integration():
    """测试7: 完整行程校验集成"""
    print("\n=== 测试7: 完整行程校验集成 ===")
    
    # 先整合行程
    agent_results = {
        "attraction": {
            "attractions": [
                {"name": "故宫", "ticket_price": 60, "visit_time_slot": "morning", 
                 "location": {"lat": 39.916, "lng": 116.397}},
                {"name": "颐和园", "ticket_price": 30, "visit_time_slot": "afternoon",
                 "location": {"lat": 39.998, "lng": 116.275}}
            ]
        },
        "accommodation": {
            "hotels": [{"name": "酒店", "price_per_night": 600}]
        },
        "food": {
            "restaurants": [
                {"name": "餐厅", "avg_price_per_person": 120}
            ]
        },
        "transport": {"transport_options": []}
    }
    
    structured_requirement = {
        "city_name": "北京",
        "travel_days": 1,
        "total_budget": 2000,
        "travel_date": "2026-05-20",
        "traveler_count": 2
    }
    
    url_combine = f"{BASE_URL}/api/v1/integration/combine"
    payload = {
        "task_id": "test_validation",
        "agent_results": agent_results,
        "structured_requirement": structured_requirement
    }
    
    try:
        # 第一步：整合行程
        response = requests.post(url_combine, json=payload, timeout=10)
        result = response.json()
        
        if result.get('code') != 200:
            print(f"✗ 行程整合失败: {result.get('msg')}")
            return False
        
        data = result.get('data', {})
        validation = data.get('validation', {})
        
        print("✓ 行程整合成功")
        print(f"  是否有效: {validation.get('valid', False)}")
        print(f"  冲突数: {len(validation.get('conflicts', []))}")
        print(f"  建议数: {len(validation.get('suggestions', []))}")
        print(f"  总花费: {data.get('total_cost', 0)} 元")
        
        # 显示冲突和建议
        if validation.get('conflicts'):
            print("  冲突详情:")
            for conflict in validation['conflicts']:
                print(f"    - [{conflict['severity']}] {conflict['description']}")
        
        if validation.get('suggestions'):
            print("  建议:")
            for suggestion in validation['suggestions']:
                print(f"    - {suggestion}")
        
        # 检查校验结果是否合理
        if validation.get('valid') is not None:
            print("✓ 校验功能正常工作")
            return True
        else:
            print("✗ 校验结果缺失")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("协调层整体测试与Bug修复验证")
    print("=" * 70)
    
    # 检查服务是否运行
    try:
        health_response = requests.get(f"{BASE_URL}/api/v1/health", timeout=3)
        if health_response.status_code != 200:
            print("⚠ 警告: 服务可能未正常运行")
            exit(1)
    except:
        print("⚠ 警告: 无法连接到服务，请先启动后端服务")
        print(f"  运行命令: python src/index.py")
        exit(1)
    
    # 执行测试
    tests = [
        ("时间冲突检测", test_time_conflict_detection),
        ("无冲突行程", test_no_time_conflict),
        ("预算校验", test_budget_validation),
        ("空数据处理", test_empty_data_handling),
        ("多天行程分配", test_multi_day_distribution),
        ("路线优化质量", test_route_optimization_quality),
        ("完整行程校验", test_itinerary_validation_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ 测试 '{test_name}' 发生异常: {str(e)}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 70)
    print("测试结果总结")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！协调层功能正常")
    else:
        print(f"\n⚠ 有 {total - passed} 个测试失败，需要修复bug")
        print("\n建议修复方向:")
        if any(name == "时间冲突检测" and not result for name, result in results):
            print("  - 检查时间冲突检测算法的重叠判断逻辑")
        if any(name == "预算校验" and not result for name, result in results):
            print("  - 检查预算计算是否正确累加各项费用")
        if any(name == "空数据处理" and not result for name, result in results):
            print("  - 增加对空数据的容错处理")
        if any(name == "多天行程分配" and not result for name, result in results):
            print("  - 优化景点到多天的分配算法")
        if any(name == "路线优化质量" and not result for name, result in results):
            print("  - 改进路线优化算法的排序逻辑")
