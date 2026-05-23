@echo off
chcp 65001 >nul
echo ========================================
echo   修复依赖冲突并安装
echo ========================================
echo.

echo [步骤 1/3] 清理npm缓存...
call npm cache clean --force
echo ✅ 缓存清理完成

echo.
echo [步骤 2/3] 删除旧的node_modules和package-lock.json...
if exist "node_modules\" rmdir /s /q node_modules
if exist "package-lock.json" del package-lock.json
echo ✅ 旧文件已删除

echo.
echo [步骤 3/3] 重新安装依赖（使用--legacy-peer-deps）...
call npm install --legacy-peer-deps

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   ✅ 依赖安装成功！
    echo ========================================
    echo.
    echo 现在可以运行以下命令启动项目：
    echo   npm run dev
    echo.
    echo 或使用一键启动脚本：
    echo   run_test.bat
    echo.
) else (
    echo.
    echo ========================================
    echo   ❌ 依赖安装失败
    echo ========================================
    echo.
    echo 尝试以下解决方案：
    echo 1. 检查网络连接
    echo 2. 使用淘宝镜像：npm config set registry https://registry.npmmirror.com
    echo 3. 查看错误日志获取详细信息
    echo.
)

pause
