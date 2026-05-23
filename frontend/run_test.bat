@echo off
chcp 65001 >nul
echo ========================================
echo   旅游行程规划系统 - 完整测试脚本
echo ========================================
echo.

echo [步骤 1/4] 检查后端服务状态...
netstat -ano | findstr :9091 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ 后端服务正在运行（端口 9091）
) else (
    echo ⚠️  后端服务未运行，正在启动...
    start "后端服务" cmd /k "cd .. && python src\index.py"
    echo 等待后端服务启动（5秒）...
    timeout /t 5 /nobreak >nul
)

echo.
echo [步骤 2/4] 检查前端依赖...
if exist "node_modules\" (
    echo ✅ 前端依赖已安装
) else (
    echo ⚠️  前端依赖未安装，正在安装...
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ 依赖安装失败！
        pause
        exit /b 1
    )
    echo ✅ 依赖安装成功
)

echo.
echo [步骤 3/4] 启动前端开发服务器...
start "前端服务" cmd /k "npm run dev"
echo 等待前端服务启动（3秒）...
timeout /t 3 /nobreak >nul

echo.
echo [步骤 4/4] 打开浏览器进行测试...
start http://localhost:3000/requirement

echo.
echo ========================================
echo   ✅ 测试环境已就绪！
echo ========================================
echo.
echo 📍 访问地址：
echo   前端应用: http://localhost:3000
echo   需求表单: http://localhost:3000/requirement
echo   后端API文档: http://127.0.0.1:9091/docs
echo.
echo 📝 测试清单：
echo   1. 填写需求表单（城市、日期、天数、预算等）
echo   2. 点击"开始智能规划"按钮
echo   3. 观察任务进度页面
echo   4. 查看生成的行程详情
echo.
echo 🔍 调试技巧：
echo   - 按 F12 打开开发者工具
echo   - 查看 Console 标签的日志
echo   - 查看 Network 标签的API请求
echo.
echo ⚠️  注意事项：
echo   - 确保所有必填字段都已填写
echo   - 预算最低为1000元
echo   - 日期不能选择过去的日期
echo.

pause
