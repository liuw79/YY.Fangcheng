cd "c:\Users\28919\SynologyDrive\0050Project\YY.Fangcheng"
python -m http.server 8080

# 学方程小游戏 🎯

一个通过有趣的游戏学习方程知识的教育项目。

## 项目简介

这是一个渐进式开发的数学教育游戏，通过不同的游戏模块帮助学生理解和掌握方程的基本概念。

## 游戏模块

### 1. ⚖️ 天平游戏
- 通过天平平衡学习等式概念
- 理解左右两边相等的含义
- 培养等式思维

### 2. 🎁 魔法盒子
- 通过魔法盒子游戏学习未知数概念
- 培养逆向思维能力
- 理解变量的含义

### 3. 📚 故事方程
- 通过故事情境学习列方程
- 解决实际问题
- 培养数学建模能力

### 4. 🏆 挑战关卡（开发中）
- 综合运用所学知识
- 挑战更复杂的方程问题

## 项目结构

```
YY.Fangcheng/
├── README.md                 # 项目说明文档
├── index.html               # 主游戏文件
├── index_simple.html        # 简化版本
├── index_step4.html         # 第四步重构版本
├── index_step5.html         # 第五步：故事方程版本
├── simple_test.html         # 测试文件
├── push_to_github.sh        # GitHub自动推送脚本
├── start_server.sh          # 服务器启动脚本
├── css/                     # 样式文件目录
│   ├── style.css
│   └── animations.css
├── js/                      # JavaScript文件目录
│   ├── game.js
│   ├── balance.js
│   ├── magicbox.js
│   ├── story.js
│   ├── levels.js
│   └── utils.js
└── docs/                    # 文档目录
    └── design.md
```

## 快速开始

### 1. 本地运行

#### 方法一：使用Python内置服务器
```bash
# 进入项目目录
cd YY.Fangcheng

# 启动HTTP服务器
python3 -m http.server 8080

# 在浏览器中访问
open http://localhost:8080/index_step5.html
```

#### 方法二：使用提供的启动脚本
```bash
# 给脚本添加执行权限
chmod +x start_server.sh

# 运行启动脚本
./start_server.sh
```

### 2. 游戏版本说明

- **index.html**: 完整版本（包含所有功能）
- **index_simple.html**: 简化版本（基础功能）
- **index_step4.html**: 第四步重构版本（天平+魔法盒子）
- **index_step5.html**: 第五步版本（添加故事方程）

推荐使用 `index_step5.html` 体验最新功能。

## GitHub自动推送脚本

项目包含一个自动推送到GitHub的脚本，可以简化代码提交和推送过程。

### 使用方法

```bash
# 给脚本添加执行权限（首次使用）
chmod +x push_to_github.sh

# 推送代码到GitHub
./push_to_github.sh "你的提交信息"
```

### 脚本功能

- ✅ 自动检测Git仓库状态
- ✅ 自动初始化Git仓库（如果需要）
- ✅ 自动配置远程仓库
- ✅ 自动添加所有文件到暂存区
- ✅ 自动提交更改
- ✅ 自动拉取最新更改
- ✅ 自动推送到远程仓库
- ✅ 彩色输出，清晰显示操作状态
- ✅ 错误处理和用户提示

### 首次使用GitHub推送

如果这是一个新项目，脚本会引导你完成以下步骤：

1. 初始化Git仓库
2. 配置GitHub远程仓库URL
3. 推送代码到GitHub

### 示例

```bash
# 推送新功能
./push_to_github.sh "添加故事方程游戏功能"

# 推送bug修复
./push_to_github.sh "修复天平游戏显示问题"

# 推送文档更新
./push_to_github.sh "更新README文档"
```

## 开发进度

- [x] 第一步：基础框架搭建
- [x] 第二步：天平游戏实现
- [x] 第三步：魔法盒子游戏实现
- [x] 第四步：代码重构和优化
- [x] 第五步：故事方程游戏实现
- [x] GitHub自动推送脚本
- [ ] 第六步：挑战关卡实现
- [ ] 第七步：用户进度保存
- [ ] 第八步：音效和动画优化

## 技术栈

- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **样式**: CSS Grid, Flexbox, CSS动画
- **部署**: 静态文件服务器
- **版本控制**: Git
- **代码托管**: GitHub

## 浏览器兼容性

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

或者直接使用提供的自动推送脚本：
```bash
./push_to_github.sh "Add some AmazingFeature"
```

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 创建 Issue
- 发起 Pull Request
- 邮件联系项目维护者

## 致谢

感谢所有为这个项目做出贡献的开发者和测试者！

---

**享受学习方程的乐趣！** 🎉