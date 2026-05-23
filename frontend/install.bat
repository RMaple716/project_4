@echo off
echo ========================================
echo   旅游行程规划系统 - 前端项目安装脚本
echo ========================================
echo.

cd frontend

echo [1/3] 检查Node.js是否安装...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 错误: 未检测到Node.js，请先安装Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)
echo ✅ Node.js已安装

echo.
echo [2/3] 检查npm版本...
node --version
npm --version

echo.
echo [3/3] 安装依赖包（这可能需要几分钟）...
echo 提示: 如果下载速度慢，可以使用淘宝镜像
echo.

npm install

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   ✅ 依赖安装成功！
    echo ========================================
    echo.
    echo 下一步操作:
    echo 1. 在新终端启动后端服务: python src\index.py
    echo 2. 在当前目录运行: npm run dev
    echo 3. 打开浏览器访问: http://localhost:3000
    echo.
) else (
    echo.
    echo ========================================
    echo   ❌ 依赖安装失败
    echo ========================================
    echo.
    echo 建议解决方案:
    echo 1. 清除缓存: npm cache clean --force
    echo 2. 使用淘宝镜像: npm config set registry https://registry.npmmirror.com
    echo 3. 重新安装: npm install
    echo.
)

pause
