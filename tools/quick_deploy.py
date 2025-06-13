#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速部署脚本 - 专门用于快速部署到服务器
简化版本，去除复杂功能，专注于快速发布
"""

import os
import sys
import json
import subprocess
import logging
import paramiko
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quick_deploy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class QuickDeploy:
    def __init__(self, config_path: str = 'tools/config.json'):
        """初始化快速部署器"""
        self.config = self._load_config(config_path)
        self.ssh_client = None
        self.sftp_client = None

    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"配置文件未找到: {config_path}")
            sys.exit(1)
        except json.JSONDecodeError:
            logger.error(f"配置文件JSON格式错误: {config_path}")
            sys.exit(1)

    def connect_ssh(self) -> None:
        """建立SSH连接"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 尝试使用SSH密钥连接
            try:
                self.ssh_client.connect(
                    hostname=self.config['server']['host'],
                    username=self.config['server']['username'],
                    key_filename=os.path.expanduser(self.config['server']['key_path'])
                )
                logger.info("SSH密钥连接成功")
            except:
                # 如果密钥连接失败，提示输入密码
                password = input(f"请输入 {self.config['server']['username']}@{self.config['server']['host']} 的密码: ")
                self.ssh_client.connect(
                    hostname=self.config['server']['host'],
                    username=self.config['server']['username'],
                    password=password
                )
                logger.info("SSH密码连接成功")
            
            self.sftp_client = self.ssh_client.open_sftp()
            
        except Exception as e:
            logger.error(f"SSH连接失败: {str(e)}")
            sys.exit(1)

    def check_port(self) -> bool:
        """检查端口是否可用"""
        try:
            port = self.config['app']['port']
            stdin, stdout, stderr = self.ssh_client.exec_command(f"netstat -tuln | grep ':{port}'")
            result = stdout.read().decode().strip()
            
            if result:
                logger.warning(f"端口 {port} 已被占用: {result}")
                return False
            else:
                logger.info(f"端口 {port} 可用")
                return True
                
        except Exception as e:
            logger.error(f"端口检查失败: {str(e)}")
            return False

    def create_deployment_package(self) -> str:
        """创建部署包"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            package_name = f"fangcheng_deploy_{timestamp}.tar.gz"
            
            # 排除不需要的文件
            exclude_files = [
                '--exclude=node_modules',
                '--exclude=.git',
                '--exclude=*.log',
                '--exclude=.DS_Store',
                '--exclude=backup',
                '--exclude=*.tar.gz'
            ]
            
            cmd = ['tar', '-czf', package_name] + exclude_files + ['.']
            subprocess.run(cmd, check=True)
            
            logger.info(f"部署包创建成功: {package_name}")
            return package_name
            
        except Exception as e:
            logger.error(f"创建部署包失败: {str(e)}")
            sys.exit(1)

    def upload_and_extract(self, package_name: str) -> None:
        """上传并解压部署包"""
        try:
            app_dir = self.config['server']['app_dir']
            temp_dir = self.config['server']['temp_dir']
            
            # 创建目录
            self.ssh_client.exec_command(f"mkdir -p {app_dir}")
            self.ssh_client.exec_command(f"mkdir -p {temp_dir}")
            
            # 上传文件
            remote_package = f"{temp_dir}/{package_name}"
            logger.info(f"上传文件到服务器: {remote_package}")
            self.sftp_client.put(package_name, remote_package)
            
            # 解压到应用目录
            logger.info(f"解压到应用目录: {app_dir}")
            self.ssh_client.exec_command(f"tar -xzf {remote_package} -C {app_dir}")
            
            # 清理临时文件
            self.ssh_client.exec_command(f"rm {remote_package}")
            os.remove(package_name)
            
            logger.info("文件上传和解压完成")
            
        except Exception as e:
            logger.error(f"上传和解压失败: {str(e)}")
            sys.exit(1)

    def setup_node_server(self) -> None:
        """设置Node.js服务器"""
        try:
            app_dir = self.config['server']['app_dir']
            port = self.config['app']['port']
            
            # 检查是否有package.json，如果没有则创建简单的服务器
            stdin, stdout, stderr = self.ssh_client.exec_command(f"test -f {app_dir}/package.json && echo 'exists'")
            has_package_json = stdout.read().decode().strip() == 'exists'
            
            if not has_package_json:
                # 创建简单的Node.js服务器
                server_js = f"""
const express = require('express');
const path = require('path');
const app = express();
const PORT = {port};

// 静态文件服务
app.use(express.static('.'));

// 默认路由
app.get('/', (req, res) => {{
    res.sendFile(path.join(__dirname, 'index.html'));
}});

// 健康检查
app.get('/health', (req, res) => {{
    res.json({{ status: 'ok', timestamp: new Date().toISOString() }});
}});

app.listen(PORT, () => {{
    console.log(`服务器运行在端口 ${{PORT}}`);
}});
"""
                
                # 写入服务器文件
                with open('temp_server.js', 'w') as f:
                    f.write(server_js)
                
                self.sftp_client.put('temp_server.js', f"{app_dir}/server.js")
                os.remove('temp_server.js')
                
                # 创建package.json
                package_json = {
                    "name": "fangcheng-app",
                    "version": "1.0.0",
                    "description": "方程游戏应用",
                    "main": "server.js",
                    "scripts": {
                        "start": "node server.js"
                    },
                    "dependencies": {
                        "express": "^4.18.0"
                    }
                }
                
                with open('temp_package.json', 'w') as f:
                    json.dump(package_json, f, indent=2)
                
                self.sftp_client.put('temp_package.json', f"{app_dir}/package.json")
                os.remove('temp_package.json')
            
            # 安装依赖
            logger.info("安装Node.js依赖...")
            stdin, stdout, stderr = self.ssh_client.exec_command(f"cd {app_dir} && npm install")
            output = stdout.read().decode()
            error = stderr.read().decode()
            
            if error and "warn" not in error.lower():
                logger.warning(f"npm install警告: {error}")
            
            logger.info("Node.js服务器设置完成")
            
        except Exception as e:
            logger.error(f"Node.js服务器设置失败: {str(e)}")
            sys.exit(1)

    def start_application(self) -> None:
        """启动应用"""
        try:
            app_dir = self.config['server']['app_dir']
            port = self.config['app']['port']
            
            # 停止可能存在的进程
            self.ssh_client.exec_command(f"pkill -f 'node.*server.js'")
            
            # 启动应用（后台运行）
            logger.info(f"启动应用在端口 {port}...")
            self.ssh_client.exec_command(f"cd {app_dir} && nohup npm start > app.log 2>&1 &")
            
            # 等待启动
            import time
            time.sleep(3)
            
            # 检查进程是否启动
            stdin, stdout, stderr = self.ssh_client.exec_command(f"ps aux | grep 'node.*server.js' | grep -v grep")
            process = stdout.read().decode().strip()
            
            if process:
                logger.info("应用启动成功!")
                logger.info(f"访问地址: http://{self.config['server']['host']}:{port}")
            else:
                logger.error("应用启动失败，请检查日志")
                
        except Exception as e:
            logger.error(f"启动应用失败: {str(e)}")
            sys.exit(1)

    def health_check(self) -> bool:
        """健康检查"""
        try:
            import requests
            url = f"http://{self.config['server']['host']}:{self.config['app']['port']}/health"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                logger.info("健康检查通过")
                return True
            else:
                logger.warning(f"健康检查失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"健康检查失败: {str(e)}")
            return False

    def cleanup(self) -> None:
        """清理资源"""
        if self.sftp_client:
            self.sftp_client.close()
        if self.ssh_client:
            self.ssh_client.close()

    def deploy(self) -> None:
        """执行完整部署流程"""
        try:
            logger.info("开始快速部署...")
            
            # 1. 连接SSH
            self.connect_ssh()
            
            # 2. 检查端口
            if not self.check_port():
                logger.warning("端口被占用，但继续部署...")
            
            # 3. 创建部署包
            package_name = self.create_deployment_package()
            
            # 4. 上传和解压
            self.upload_and_extract(package_name)
            
            # 5. 设置Node.js服务器
            self.setup_node_server()
            
            # 6. 启动应用
            self.start_application()
            
            # 7. 健康检查
            import time
            time.sleep(5)  # 等待应用完全启动
            if self.health_check():
                logger.info("部署成功完成!")
            else:
                logger.info("部署完成，但健康检查未通过，请手动检查")
            
            logger.info(f"应用访问地址: http://{self.config['server']['host']}:{self.config['app']['port']}")
            
        except Exception as e:
            logger.error(f"部署失败: {str(e)}")
            sys.exit(1)
        finally:
            self.cleanup()

def main():
    deployer = QuickDeploy()
    deployer.deploy()

if __name__ == '__main__':
    main() 