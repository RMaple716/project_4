"""测试数据库连接 - 增强版"""
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def test_connection():
    """测试数据库连接"""
    print("=" * 50)
    print("🔍 开始测试 PostgreSQL 数据库连接...")
    print("=" * 50)
    
    # 获取数据库URL
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:123456@localhost:5432/postgres"
    )
    
    print(f"\n📌 数据库连接字符串: {database_url}")
    print(f"📌 编码: UTF-8")
    
    try:
        # 创建引擎
        engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            echo=False
        )
        
        # 尝试连接数据库
        with engine.connect() as conn:
            # 执行一个简单的查询
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            
            print("\n✅ 数据库连接成功！")
            print(f"📌 PostgreSQL 版本: {version}")
            
            # 获取当前数据库名称
            result = conn.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            print(f"📌 当前数据库: {db_name}")
            
            # 获取当前用户
            result = conn.execute(text("SELECT current_user;"))
            user = result.fetchone()[0]
            print(f"📌 当前用户: {user}")
            
            print("\n" + "=" * 50)
            print("✨ 所有测试通过！数据库配置正确。")
            print("=" * 50)
            return True
            
    except UnicodeDecodeError as e:
        print(f"\n❌ 编码错误！")
        print(f"错误信息: {str(e)}")
        print("\n" + "=" * 50)
        print("🔧 可能原因：")
        print("=" * 50)
        print("1. PostgreSQL 服务未启动或无法连接")
        print("2. 数据库返回的错误消息包含非UTF-8字符（通常是GBK中文）")
        print("3. 密码错误或数据库不存在")
        print("\n💡 解决方案：")
        print("- 检查 PostgreSQL 服务是否运行")
        print("- 确认用户名和密码正确")
        print("- 确认数据库 'travel' 已创建")
        print("- 尝试使用 pgAdmin 或其他工具手动连接测试")
        print("=" * 50)
        return False
        
    except OperationalError as e:
        print(f"\n❌ 数据库操作错误！")
        print(f"错误信息: {str(e)}")
        print("\n" + "=" * 50)
        print("🔧 请检查以下事项：")
        print("=" * 50)
        print("1. PostgreSQL 服务是否已启动？")
        print("   - Windows: 任务管理器 → 服务 → 查找 postgresql")
        print("   - 或运行: services.msc 查看 PostgreSQL 服务状态")
        print("\n2. 用户名和密码是否正确？")
        print("   - 默认用户名: postgres")
        print("   - 密码是安装时设置的")
        print("\n3. 数据库 'travel' 是否已创建？")
        print("   - 打开 pgAdmin 4 或使用命令行创建")
        print("   - SQL: CREATE DATABASE travel;")
        print("\n4. 端口是否为 5432？")
        print("   - 默认端口是 5432")
        print("   - 如果修改过，请更新配置文件")
        print("\n5. 防火墙是否阻止连接？")
        print("   - 本地开发通常不需要特殊配置")
        print("=" * 50)
        return False
        
    except Exception as e:
        print(f"\n❌ 数据库连接失败！")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print("\n" + "=" * 50)
        print("🔧 请检查以下事项：")
        print("=" * 50)
        print("1. PostgreSQL 服务是否已启动？")
        print("   - Windows: 任务管理器 → 服务 → 查找 postgresql")
        print("   - 或运行: services.msc 查看 PostgreSQL 服务状态")
        print("\n2. 用户名和密码是否正确？")
        print("   - 默认用户名: postgres")
        print("   - 密码是安装时设置的")
        print("\n3. 数据库 'travel' 是否已创建？")
        print("   - 打开 pgAdmin 4 或使用命令行创建")
        print("   - SQL: CREATE DATABASE travel;")
        print("\n4. 端口是否为 5432？")
        print("   - 默认端口是 5432")
        print("   - 如果修改过，请更新配置文件")
        print("\n5. 防火墙是否阻止连接？")
        print("   - 本地开发通常不需要特殊配置")
        print("=" * 50)
        return False

if __name__ == "__main__":
    test_connection()
