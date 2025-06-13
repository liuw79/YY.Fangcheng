#!/bin/bash

# 自动推送到GitHub的脚本
# 使用方法: ./push_to_github.sh "提交信息"

# 显示彩色输出的函数
function echo_color() {
    local color=$1
    local message=$2
    case $color in
        "green") echo -e "\033[32m${message}\033[0m" ;;
        "red") echo -e "\033[31m${message}\033[0m" ;;
        "yellow") echo -e "\033[33m${message}\033[0m" ;;
        "blue") echo -e "\033[34m${message}\033[0m" ;;
        *) echo "$message" ;;
    esac
}

# 检查是否提供了提交信息
if [ -z "$1" ]; then
    echo_color "red" "错误: 请提供提交信息"
    echo "使用方法: ./push_to_github.sh \"提交信息\""
    exit 1
fi

COMMIT_MESSAGE="$1"

# 检查是否在Git仓库中
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo_color "red" "错误: 当前目录不是Git仓库"
    
    # 询问是否要初始化Git仓库
    read -p "是否要初始化Git仓库? (y/n): " INIT_REPO
    if [[ $INIT_REPO == "y" || $INIT_REPO == "Y" ]]; then
        echo_color "blue" "初始化Git仓库..."
        git init
        
        # 询问GitHub仓库URL
        read -p "请输入GitHub仓库URL: " REPO_URL
        if [ -z "$REPO_URL" ]; then
            echo_color "red" "错误: 未提供GitHub仓库URL"
            exit 1
        fi
        
        # 添加远程仓库
        echo_color "blue" "添加远程仓库..."
        git remote add origin $REPO_URL
    else
        echo_color "yellow" "操作已取消"
        exit 0
    fi
fi

# 检查远程仓库是否已配置
if ! git remote -v | grep -q origin; then
    echo_color "red" "错误: 未配置远程仓库"
    
    # 询问GitHub仓库URL
    read -p "请输入GitHub仓库URL: " REPO_URL
    if [ -z "$REPO_URL" ]; then
        echo_color "red" "错误: 未提供GitHub仓库URL"
        exit 1
    fi
    
    # 添加远程仓库
    echo_color "blue" "添加远程仓库..."
    git remote add origin $REPO_URL
fi

# 显示当前状态
echo_color "blue" "当前Git状态:"
git status

# 添加所有文件到暂存区
echo_color "blue" "添加文件到暂存区..."
git add .

# 提交更改
echo_color "blue" "提交更改..."
git commit -m "$COMMIT_MESSAGE"

# 获取当前分支名称
CURRENT_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null)
if [ -z "$CURRENT_BRANCH" ]; then
    CURRENT_BRANCH="main"
    echo_color "yellow" "未检测到分支名称，使用默认分支: $CURRENT_BRANCH"
fi

# 检查远程分支是否存在
if ! git ls-remote --heads origin $CURRENT_BRANCH | grep -q $CURRENT_BRANCH; then
    echo_color "yellow" "远程分支 $CURRENT_BRANCH 不存在，将创建新分支"
    
    # 推送到远程仓库并设置上游分支
    echo_color "blue" "推送到远程仓库..."
    git push -u origin $CURRENT_BRANCH
else
    # 拉取最新更改
    echo_color "blue" "拉取最新更改..."
    git pull origin $CURRENT_BRANCH
    
    # 处理可能的合并冲突
    if [ $? -ne 0 ]; then
        echo_color "red" "拉取过程中出现冲突，请手动解决冲突后再次运行此脚本"
        exit 1
    fi
    
    # 推送到远程仓库
    echo_color "blue" "推送到远程仓库..."
    git push origin $CURRENT_BRANCH
fi

# 检查推送是否成功
if [ $? -eq 0 ]; then
    echo_color "green" "成功推送到GitHub！"
    echo_color "green" "分支: $CURRENT_BRANCH"
    echo_color "green" "提交信息: $COMMIT_MESSAGE"
    
    # 显示远程仓库URL
    REMOTE_URL=$(git remote get-url origin)
    echo_color "green" "远程仓库: $REMOTE_URL"
else
    echo_color "red" "推送失败，请检查错误信息"
fi