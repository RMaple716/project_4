@echo off
chcp 65001 >nul
echo ========================================
echo   快速测试指南
echo ========================================
echo.

echo 📋 测试步骤：
echo.
echo 1️⃣  启动后端服务（如果还未启动）
echo    在新终端运行: python src\index.py
echo.
echo 2️⃣  安装前端依赖（如果还未安装）
echo    cd frontend
echo    npm install
echo.
echo 3️⃣  启动前端开发服务器
echo    cd frontend
echo    npm run dev
echo.
echo 4️⃣  打开浏览器访问
echo    http://localhost:3000/requirement
echo.
echo 5️⃣  填写表单并测试
echo    - 城市: 北京
echo    - 日期: 选择未来日期
echo    - 天数: 3
echo    - 人数: 2
echo    - 预算: 5000
echo    - 偏好: 历史古迹、美食探索
echo    - 点击"开始智能规划"
echo.
echo 6️⃣  观察结果
echo    - 应该看到成功提示
echo    - 自动跳转到任务状态页
echo    - 进度条逐渐增长
echo    - 完成后显示"查看行程"按钮
echo.
echo 🔍 调试方法：
echo    - 按 F12 打开开发者工具
echo    - 查看 Console 标签的日志
echo    - 查看 Network 标签的API请求
echo.
echo 📖 详细测试文档：
echo    - MANUAL_TEST_GUIDE.md (完整测试指南)
echo    - REQUIREMENT_FORM_TEST.md (测试用例)
echo    - test_api_integration.py (API自动化测试)
echo.
echo 💡 一键启动：
echo    运行 run_test.bat 自动完成所有步骤
echo.

pause
