#!/bin/bash

# 学方程小游戏 - 服务器启动脚本
# 自动启动HTTP服务器并打开浏览器

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印彩色信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # 端口被占用
    else
        return 1  # 端口可用
    fi
}

# 查找可用端口
find_available_port() {
    local start_port=8080
    local max_port=8090
    
    for ((port=start_port; port<=max_port; port++)); do
        if ! check_port $port; then
            echo $port
            return 0
        fi
    done
    
    return 1
}

# 主函数
main() {
    print_info "学方程小游戏 - 服务器启动脚本"
    echo "==========================================="
    
    # 检查是否在正确的目录
    if [ ! -f "index.html" ]; then
        print_error "未找到游戏文件，请确保在项目根目录运行此脚本"
        exit 1
    fi
    
    # 查找可用端口
    print_info "正在查找可用端口..."
    PORT=$(find_available_port)
    
    if [ $? -ne 0 ]; then
        print_error "无法找到可用端口 (8080-8090)，请手动检查端口占用情况"
        exit 1
    fi
    
    print_success "找到可用端口: $PORT"
    
    # 检查Python版本
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "未找到Python，请安装Python后重试"
        exit 1
    fi
    
    print_info "使用 $PYTHON_CMD 启动HTTP服务器..."
    
    # 启动服务器
    print_info "正在启动服务器，端口: $PORT"
    print_info "按 Ctrl+C 停止服务器"
    echo "==========================================="
    
    # 延迟打开浏览器
    (
        sleep 2
        if command -v open &> /dev/null; then
            # macOS
            open "http://localhost:$PORT/index.html"
        elif command -v xdg-open &> /dev/null; then
            # Linux
            xdg-open "http://localhost:$PORT/index.html"
        elif command -v start &> /dev/null; then
            # Windows
            start "http://localhost:$PORT/index.html"
        else
            print_warning "无法自动打开浏览器，请手动访问: http://localhost:$PORT/index.html"
        fi
    ) &
    
    # 启动HTTP服务器
    $PYTHON_CMD -m http.server $PORT
}

# 信号处理
trap 'print_info "\n正在停止服务器..."; exit 0' INT

# 运行主函数
main "$@"