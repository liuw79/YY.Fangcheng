@echo off
chcp 65001 >nul
echo ====================================
echo     GitHub 连接设置脚本
echo ====================================
echo.

echo 当前项目已初始化为Git仓库，但尚未连接到GitHub。
echo.
echo 请按照以下步骤手动设置GitHub连接：
echo.
echo 1. 在GitHub上创建新仓库：
echo    - 访问 https://github.com/new
echo    - 仓库名称：YY.Fangcheng
echo    - 描述：学方程小游戏 - 一个帮助学生学习数学方程的互动游戏
echo    - 选择公开或私有
echo    - 不要初始化README（本地已有文件）
echo.
echo 2. 复制仓库URL（例如：https://github.com/用户名/YY.Fangcheng.git）
echo.
echo 3. 在下方输入仓库URL：
set /p REPO_URL="请输入GitHub仓库URL: "

if "%REPO_URL%"=="" (
    echo 错误：未输入仓库URL
    pause
    exit /b 1
)

echo.
echo 正在配置远程仓库...
git remote add origin %REPO_URL%

if %errorlevel% neq 0 (
    echo 错误：添加远程仓库失败
    pause
    exit /b 1
)

echo 成功添加远程仓库！
echo.
echo 正在添加文件到暂存区...
git add .

echo 正在提交更改...
git commit -m "初始提交：学方程小游戏项目"

echo 正在推送到GitHub...
git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo 推送失败，可能需要先设置分支：
    echo git branch -M main
    echo git push -u origin main
    echo.
    echo 或者检查是否需要身份验证。
    pause
    exit /b 1
)

echo.
echo ====================================
echo     GitHub连接设置完成！
echo ====================================
echo.
echo 远程仓库：%REPO_URL%
echo 本地分支：main
echo.
echo 现在可以使用以下命令进行后续操作：
echo   git status    - 查看状态
echo   git add .     - 添加文件
echo   git commit -m "提交信息" - 提交更改
echo   git push      - 推送到GitHub
echo   git pull      - 从GitHub拉取更新
echo.
pause