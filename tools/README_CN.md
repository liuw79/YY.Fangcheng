# 自动化部署工具

这个目录包含了一套完整的工具，用于自动化部署、备份、监控和发布管理您的应用程序。

## 前置要求

1. Python 3.8 或更高版本
2. 服务器SSH访问权限
3. GitHub账户和仓库访问权限
4. 服务器上安装Nginx（用于反向代理）

## 安装

1. 安装Python依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 设置环境变量：
   ```bash
   export GITHUB_TOKEN=你的github令牌
   ```

3. 在 `config.json` 中配置部署设置：
   ```json
   {
       "server": {
           "host": "op.gaowei.com",
           "username": "root",
           "key_path": "~/.ssh/id_rsa",
           "app_dir": "/var/www/fangcheng",
           "temp_dir": "/tmp",
           "domain": "op.gaowei.com",
           "port": 8888
       },
       "backup": {
           "remote_dir": "/var/backups/fangcheng",
           "local_dir": "./backups",
           "retention_days": 7
       },
       "github": {
           "repo": "你的用户名/你的仓库",
           "branch": "main"
       },
       "app": {
           "name": "fangcheng",
           "port": 8888
       }
   }
   ```

## 可用工具

### 1. 快速部署脚本 (`quick_deploy.py`)

专门用于快速部署到服务器的简化版本：
- SSH连接到服务器
- 端口检查
- 应用部署
- Node.js服务器设置
- 健康检查

使用方法：
```bash
python tools/quick_deploy.py
```

### 2. 完整部署脚本 (`deploy.py`)

处理完整的部署流程：
- SSH连接到服务器
- 端口可用性检查
- 应用部署
- Nginx配置
- 健康检查

使用方法：
```bash
python tools/deploy.py [--config 配置文件]
```

### 3. 备份脚本 (`backup.py`)

管理应用备份：
- 完整应用备份
- 仅数据备份
- 仅配置备份
- 备份轮换
- 恢复功能

使用方法：
```bash
python tools/backup.py [--config 配置文件] [--type {full,data,config}] [--restore 备份名称] [--list] [--cleanup]
```

### 4. 健康检查脚本 (`health_check.py`)

监控应用健康状态：
- HTTP端点检查
- 进程监控
- 资源使用跟踪
- 日志分析
- 失败时自动重启

使用方法：
```bash
python tools/health_check.py [--config 配置文件] [--auto-restart] [--continuous] [--interval 秒数]
```

### 5. GitHub自动化 (`github_automation.py`)

管理GitHub发布和变更日志：
- 版本号升级
- 变更日志生成
- 发布创建
- 标签管理

使用方法：
```bash
python tools/github_automation.py [--config 配置文件] [--bump {major,minor,patch}] [--skip-push] [--skip-release]
```

## 目录结构

```
tools/
├── README_CN.md
├── requirements.txt
├── config.json
├── quick_deploy.py      # 快速部署脚本
├── deploy.py           # 完整部署脚本
├── backup.py           # 备份脚本
├── health_check.py     # 健康检查脚本
└── github_automation.py # GitHub自动化脚本
```

## 最佳实践

1. **配置**
   - 将敏感信息保存在环境变量中
   - 使用SSH密钥进行身份验证
   - 定期更新配置文件

2. **备份**
   - 安排定期备份
   - 测试恢复程序
   - 监控备份存储使用情况

3. **部署**
   - 部署后始终运行健康检查
   - 对所有更改使用版本控制
   - 保留部署日志

4. **监控**
   - 设置持续健康检查
   - 为关键问题配置警报
   - 监控资源使用情况

## 安全考虑

1. **访问控制**
   - 使用SSH密钥而不是密码
   - 限制服务器访问权限
   - 定期轮换凭据

2. **数据保护**
   - 加密敏感数据
   - 安全备份存储
   - 实施适当的文件权限

3. **网络安全**
   - 对所有连接使用HTTPS
   - 配置防火墙规则
   - 监控可疑活动

## 故障排除

1. **部署问题**
   - 检查SSH连接
   - 验证端口可用性
   - 查看应用日志

2. **备份问题**
   - 检查磁盘空间
   - 验证备份权限
   - 测试恢复程序

3. **健康检查失败**
   - 查看应用日志
   - 检查资源使用情况
   - 验证网络连接

## 快速开始

对于急需部署的情况，使用快速部署脚本：

```bash
# 1. 确保配置文件正确
# 2. 运行快速部署
python tools/quick_deploy.py

# 应用将部署到: http://op.gaowei.com:8888
```

## 许可证

本项目采用MIT许可证 - 详情请参阅LICENSE文件。 