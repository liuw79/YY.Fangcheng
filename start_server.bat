@echo off
chcp 65001 >nul
echo ====================================
echo     学方程小游戏 - 服务器启动脚本
echo ====================================
echo.

REM 检查是否在正确的目录
if not exist "index.html" (
    echo [错误] 未找到游戏文件，请确保在项目根目录运行此脚本
    pause
    exit /b 1
)

echo [信息] 正在查找可用端口...

REM 检查端口是否可用的函数
set PORT=8080
:check_port
netstat -an | find ":%PORT% " >nul 2>&1
if %errorlevel% equ 0 (
    set /a PORT+=1
    if %PORT% leq 8090 goto check_port
    echo [错误] 无法找到可用端口 (8080-8090)
    pause
    exit /b 1
)

echo [成功] 找到可用端口: %PORT%
echo.

REM 检查Python版本
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto python_found
)

python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3
    goto python_found
)

REM 检查是否有Node.js
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [信息] 未找到Python，使用Node.js启动服务器...
    goto use_node
)

echo [错误] 未找到Python或Node.js，请安装其中一个后重试
echo.
echo 安装选项：
echo 1. Python: https://www.python.org/downloads/
echo 2. Node.js: https://nodejs.org/
pause
exit /b 1

:python_found
echo [信息] 使用 %PYTHON_CMD% 启动HTTP服务器...
echo [信息] 正在启动服务器，端口: %PORT%
echo [信息] 按 Ctrl+C 停止服务器
echo ====================================
echo.
echo 游戏地址: http://localhost:%PORT%/index.html
echo.

REM 延迟打开浏览器
start "" "http://localhost:%PORT%/index.html"

REM 启动Python HTTP服务器
%PYTHON_CMD% -m http.server %PORT%
goto end

:use_node
echo [信息] 使用Node.js启动HTTP服务器...
echo [信息] 正在启动服务器，端口: %PORT%
echo [信息] 按 Ctrl+C 停止服务器
echo ====================================
echo.
echo 游戏地址: http://localhost:%PORT%/index.html
echo.

REM 延迟打开浏览器
start "" "http://localhost:%PORT%/index.html"

REM 使用Node.js启动服务器
echo const http = require('http'); > temp_server.js
echo const fs = require('fs'); >> temp_server.js
echo const path = require('path'); >> temp_server.js
echo const url = require('url'); >> temp_server.js
echo. >> temp_server.js
echo const server = http.createServer((req, res) =^> { >> temp_server.js
echo   const parsedUrl = url.parse(req.url); >> temp_server.js
echo   let pathname = `.${parsedUrl.pathname}`; >> temp_server.js
echo   if (pathname === './') pathname = './index.html'; >> temp_server.js
echo. >> temp_server.js
echo   const ext = path.parse(pathname).ext; >> temp_server.js
echo   const map = { >> temp_server.js
echo     '.ico': 'image/x-icon', >> temp_server.js
echo     '.html': 'text/html', >> temp_server.js
echo     '.js': 'text/javascript', >> temp_server.js
echo     '.json': 'application/json', >> temp_server.js
echo     '.css': 'text/css', >> temp_server.js
echo     '.png': 'image/png', >> temp_server.js
echo     '.jpg': 'image/jpeg', >> temp_server.js
echo     '.wav': 'audio/wav', >> temp_server.js
echo     '.mp3': 'audio/mpeg', >> temp_server.js
echo     '.svg': 'image/svg+xml', >> temp_server.js
echo     '.pdf': 'application/pdf', >> temp_server.js
echo     '.doc': 'application/msword' >> temp_server.js
echo   }; >> temp_server.js
echo. >> temp_server.js
echo   fs.exists(pathname, (exist) =^> { >> temp_server.js
echo     if(!exist) { >> temp_server.js
echo       res.statusCode = 404; >> temp_server.js
echo       res.end(`File ${pathname} not found!`); >> temp_server.js
echo       return; >> temp_server.js
echo     } >> temp_server.js
echo. >> temp_server.js
echo     if (fs.statSync(pathname).isDirectory()) pathname += '/index.html'; >> temp_server.js
echo. >> temp_server.js
echo     fs.readFile(pathname, (err, data) =^> { >> temp_server.js
echo       if(err){ >> temp_server.js
echo         res.statusCode = 500; >> temp_server.js
echo         res.end(`Error getting the file: ${err}.`); >> temp_server.js
echo       } else { >> temp_server.js
echo         res.setHeader('Content-type', map[ext] \|\| 'text/plain' ); >> temp_server.js
echo         res.end(data); >> temp_server.js
echo       } >> temp_server.js
echo     }); >> temp_server.js
echo   }); >> temp_server.js
echo }); >> temp_server.js
echo. >> temp_server.js
echo server.listen(%PORT%, () =^> { >> temp_server.js
echo   console.log(`Server running at http://localhost:%PORT%/`); >> temp_server.js
echo }); >> temp_server.js

node temp_server.js
del temp_server.js >nul 2>&1

:end
echo.
echo [信息] 服务器已停止
pause