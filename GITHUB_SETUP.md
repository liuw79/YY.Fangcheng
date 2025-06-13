# GitHub 连接设置指南

## 当前状态

✅ Git仓库已初始化  
❌ 尚未连接到GitHub远程仓库

## 快速设置步骤

### 方法一：使用自动化脚本（推荐）

1. **双击运行** `setup_github.bat` 文件
2. 按照脚本提示操作
3. 在GitHub上创建仓库后，将URL粘贴到脚本中

### 方法二：手动设置

#### 步骤1：在GitHub上创建仓库

1. 访问 [GitHub新建仓库页面](https://github.com/new)
2. 填写仓库信息：
   - **仓库名称**：`YY.Fangcheng`
   - **描述**：`学方程小游戏 - 一个帮助学生学习数学方程的互动游戏`
   - **可见性**：选择公开或私有
   - **重要**：不要勾选"Initialize this repository with a README"（因为本地已有文件）

#### 步骤2：获取仓库URL

创建完成后，GitHub会显示仓库URL，格式如下：
```
https://github.com/你的用户名/YY.Fangcheng.git
```

#### 步骤3：在本地配置远程仓库

打开命令提示符或PowerShell，切换到项目目录，执行：

```bash
# 添加远程仓库
git remote add origin https://github.com/你的用户名/YY.Fangcheng.git

# 添加所有文件到暂存区
git add .

# 提交更改
git commit -m "初始提交：学方程小游戏项目"

# 设置主分支并推送
git branch -M main
git push -u origin main
```

## 验证连接

连接成功后，可以使用以下命令验证：

```bash
# 查看远程仓库配置
git remote -v

# 查看当前状态
git status

# 查看提交历史
git log --oneline
```

## 日常使用命令

### 推送更改到GitHub
```bash
git add .
git commit -m "你的提交信息"
git push
```

### 从GitHub拉取更新
```bash
git pull
```

### 查看状态
```bash
git status
```

## 故障排除

### 问题1：推送时要求身份验证

**解决方案**：
1. 使用GitHub Personal Access Token
2. 或配置SSH密钥
3. 详见：[GitHub身份验证文档](https://docs.github.com/en/authentication)

### 问题2：推送被拒绝

**可能原因**：远程仓库有更新

**解决方案**：
```bash
git pull origin main
git push origin main
```

### 问题3：合并冲突

**解决方案**：
1. 手动编辑冲突文件
2. 解决冲突后：
```bash
git add .
git commit -m "解决合并冲突"
git push
```

## 项目信息

- **项目名称**：学方程小游戏
- **技术栈**：HTML5, CSS3, JavaScript
- **游戏模块**：天平游戏、魔法盒子、故事方程
- **目标用户**：学习数学方程的学生

## 后续开发

连接GitHub后，建议：

1. **创建开发分支**：
   ```bash
   git checkout -b develop
   ```

2. **使用功能分支**：
   ```bash
   git checkout -b feature/新功能名称
   ```

3. **定期备份**：
   ```bash
   git push origin 分支名称
   ```

---

**需要帮助？** 请查看 [Git官方文档](https://git-scm.com/doc) 或 [GitHub帮助文档](https://docs.github.com/)