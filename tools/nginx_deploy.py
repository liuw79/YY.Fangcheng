#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基于Nginx的快速部署脚本
使用nginx直接服务静态文件，无需Node.js
"""

import os
import sys
import json
import subprocess
import logging
import paramiko
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nginx_deploy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class NginxDeploy:
    def __init__(self, config_path: str = 'tools/config.json'):
        """初始化nginx部署器"""
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

    def connect_ssh(self) -> None:
        """建立SSH连接"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            try:
                self.ssh_client.connect(
                    hostname=self.config['server']['host'],
                    username=self.config['server']['username'],
                    key_filename=os.path.expanduser(self.config['server']['key_path'])
                )
                logger.info("SSH密钥连接成功")
            except:
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

    def create_deployment_package(self) -> str:
        """创建部署包"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            package_name = f"fangcheng_deploy_{timestamp}.tar.gz"
            
            # 只打包静态文件
            exclude_files = [
                '--exclude=node_modules',
                '--exclude=.git',
                '--exclude=*.log',
                '--exclude=.DS_Store',
                '--exclude=backup',
                '--exclude=*.tar.gz',
                '--exclude=tools',
                '--exclude=*.py'
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

    def configure_nginx(self) -> None:
        """配置nginx"""
        try:
            app_dir = self.config['server']['app_dir']
            port = self.config['app']['port']
            domain = self.config['server']['domain']
            
            # 创建nginx配置
            nginx_config = f"""server {{
    listen {port};
    server_name {domain};
    root {app_dir};
    index index.html index.htm;

    # 静态文件缓存
    location ~* \\.(css|js|png|jpg|jpeg|gif|ico|svg)$ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}

    # 主页面
    location / {{
        try_files $uri $uri/ /index.html;
    }}

    # 健康检查
    location /health {{
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }}

    # 日志
    access_log /var/log/nginx/{self.config['app']['name']}_access.log;
    error_log /var/log/nginx/{self.config['app']['name']}_error.log;
}}"""

            # 写入nginx配置文件
            config_file = f"/etc/nginx/sites-available/{self.config['app']['name']}"
            
            # 创建临时配置文件
            with open('temp_nginx.conf', 'w') as f:
                f.write(nginx_config)
            
            # 上传配置文件
            self.sftp_client.put('temp_nginx.conf', config_file)
            os.remove('temp_nginx.conf')
            
            # 启用站点
            self.ssh_client.exec_command(f"ln -sf {config_file} /etc/nginx/sites-enabled/")
            
            # 测试nginx配置
            stdin, stdout, stderr = self.ssh_client.exec_command("nginx -t")
            error = stderr.read().decode()
            if error and "successful" not in error:
                raise Exception(f"Nginx配置测试失败: {error}")
            
            # 重新加载nginx
            self.ssh_client.exec_command("systemctl reload nginx")
            
            logger.info("Nginx配置完成")
            
        except Exception as e:
            logger.error(f"Nginx配置失败: {str(e)}")
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
            logger.info("开始基于Nginx的部署...")
            
            # 1. 连接SSH
            self.connect_ssh()
            
            # 2. 创建部署包
            package_name = self.create_deployment_package()
            
            # 3. 上传和解压
            self.upload_and_extract(package_name)
            
            # 4. 配置nginx
            self.configure_nginx()
            
            # 5. 健康检查
            import time
            time.sleep(3)  # 等待nginx重新加载
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
    deployer = NginxDeploy()
    deployer.deploy()

if __name__ == '__main__':
    main()