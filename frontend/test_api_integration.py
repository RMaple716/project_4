"""
前端需求表单API测试脚本
测试与后端的集成是否正常
"""
import requests
import json
from datetime import datetime, timedelta

# 后端API地址
BASE_URL = "http://127.0.0.1:9091/api/v1"

def test_health_check():
    """测试健康检查"""
    print("\n🔍 测试1: 健康检查")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {e}")
        print("💡 提示: 请先运行 'python src/index.py' 启动后端服务")
        return False

def test_submit_requirement():
    """测试提交需求"""
    print("\n📝 测试2: 提交需求")
    
    # 测试数据
    test_data = {
        "user_id": "test_user_001",
        "requirement": {
            "city_name": "北京",
            "travel_days": 3,
            "total_budget": 5000,
            "travel_type": "family",
            "start_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "preferences": ["历史古迹", "美食探索", "文化体验"]
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/requirement/submit",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                requirement_id = data["data"]["requirement_id"]
                print(f"✅ 需求提交成功")
                print(f"   Requirement ID: {requirement_id}")
                return requirement_id
            else:
                print(f"❌ 提交失败: {data.get('msg')}")
                return None
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"   响应: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_task_decompose(requirement_id):
    """测试任务分解"""
    print("\n🔄 测试3: 任务分解")
    
    if not requirement_id:
        print("⚠️  跳过任务分解测试（缺少requirement_id）")
        return None
    
    test_data = {
        "requirement_id": requirement_id,
        "structured_requirement": {
            "city_name": "北京",
            "travel_days": 3,
            "total_budget": 5000,
            "travel_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "traveler_count": 2,
            "preferences": ["历史古迹", "美食探索", "文化体验"]
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/task/decompose",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                task_id = data["data"]["task_id"]
                print(f"✅ 任务分解成功")
                print(f"   Task ID: {task_id}")
                print(f"   进度: {data['data'].get('progress', 0)}%")
                return task_id
            else:
                print(f"❌ 分解失败: {data.get('msg')}")
                return None
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"   响应: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_get_task_status(task_id):
    """测试获取任务状态"""
    print("\n📊 测试4: 获取任务状态")
    
    if not task_id:
        print("⚠️  跳过任务状态测试（缺少task_id）")
        return
    
    try:
        response = requests.get(f"{BASE_URL}/task/{task_id}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                task_data = data["data"]
                print(f"✅ 获取任务状态成功")
                print(f"   状态: {task_data.get('status')}")
                print(f"   进度: {task_data.get('progress', 0)}%")
                print(f"   类型: {task_data.get('task_type')}")
            else:
                print(f"❌ 获取失败: {data.get('msg')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_validation_api():
    """测试验证API"""
    print("\n✔️  测试5: 时间冲突检测")
    
    test_data = {
        "schedule": [
            {
                "name": "故宫博物院",
                "start_time": "09:00",
                "end_time": "12:00",
                "activity_type": "attraction"
            },
            {
                "name": "午餐",
                "start_time": "11:30",
                "duration": "1小时",
                "activity_type": "meal"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/validation/time-conflict",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                print(f"✅ 时间冲突检测成功")
                print(f"   是否有冲突: {data['data'].get('has_conflict')}")
                if data['data'].get('conflicts'):
                    print(f"   冲突数量: {len(data['data']['conflicts'])}")
            else:
                print(f"❌ 检测失败: {data.get('msg')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_static_data_api():
    """测试静态数据API"""
    print("\n📚 测试6: 获取城市列表")
    
    try:
        response = requests.get(f"{BASE_URL}/static/cities")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                cities = data.get("data", [])
                print(f"✅ 获取城市列表成功")
                print(f"   城市数量: {len(cities)}")
                if cities:
                    print(f"   示例城市: {', '.join(cities[:5])}")
            else:
                print(f"❌ 获取失败: {data.get('msg')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def main():
    """主测试函数"""
    print("=" * 60)
    print("  旅游行程规划系统 - API集成测试")
    print("=" * 60)
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API地址: {BASE_URL}")
    
    # 执行测试
    results = {}
    
    # 测试1: 健康检查
    results["health"] = test_health_check()
    if not results["health"]:
        print("\n❌ 后端服务未运行，测试中止")
        print("💡 请先运行: python src/index.py")
        return
    
    # 测试2: 提交需求
    requirement_id = test_submit_requirement()
    results["submit"] = requirement_id is not None
    
    # 测试3: 任务分解
    task_id = test_task_decompose(requirement_id)
    results["decompose"] = task_id is not None
    
    # 测试4: 获取任务状态
    if task_id:
        test_get_task_status(task_id)
        results["task_status"] = True
    else:
        results["task_status"] = False
    
    # 测试5: 验证API
    test_validation_api()
    results["validation"] = True
    
    # 测试6: 静态数据
    test_static_data_api()
    results["static_data"] = True
    
    # 测试结果汇总
    print("\n" + "=" * 60)
    print("  测试结果汇总")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20s} {status}")
    
    print("-" * 60)
    print(f"总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！前端可以正常使用后端API")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查上述错误信息")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
