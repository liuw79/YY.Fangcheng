#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单部署脚本 - 使用Python内置HTTP服务器
适用于快速部署，无需nginx或Node.js
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
        logging.FileHandler('simple_deploy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SimpleDeploy:
    def __init__(self, config_path: str = 'tools/config.json'):
        """初始化简单部署器"""
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

    def create_server_script(self) -> None:
        """创建Python HTTP服务器脚本"""
        try:
            app_dir = self.config['server']['app_dir']
            port = self.config['app']['port']
            
            # 创建Python HTTP服务器脚本
            server_script = f"""#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys

PORT = {port}
DIRECTORY = "{app_dir}"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'healthy\\n')
            return
        super().do_GET()

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"服务器运行在端口 {{PORT}}")
        print(f"访问地址: http://localhost:{{PORT}}")
        httpd.serve_forever()
"""
            
            # 写入服务器脚本
            with open('temp_server.py', 'w') as f:
                f.write(server_script)
            
            # 上传脚本
            self.sftp_client.put('temp_server.py', f"{app_dir}/server.py")
            os.remove('temp_server.py')
            
            # 设置执行权限
            self.ssh_client.exec_command(f"chmod +x {app_dir}/server.py")
            
            logger.info("HTTP服务器脚本创建完成")
            
        except Exception as e:
            logger.error(f"创建服务器脚本失败: {str(e)}")
            sys.exit(1)

    def start_server(self) -> None:
        """启动HTTP服务器"""
        try:
            app_dir = self.config['server']['app_dir']
            port = self.config['app']['port']
            
            # 停止可能存在的进程
            self.ssh_client.exec_command(f"pkill -f 'python.*server.py'")
            
            # 启动服务器（后台运行）
            logger.info(f"启动HTTP服务器在端口 {port}...")
            self.ssh_client.exec_command(f"cd {app_dir} && nohup python3 server.py > server.log 2>&1 &")
            
            # 等待启动
            import time
            time.sleep(3)
            
            # 检查进程是否启动
            stdin, stdout, stderr = self.ssh_client.exec_command(f"ps aux | grep 'python.*server.py' | grep -v grep")
            process = stdout.read().decode().strip()
            
            if process:
                logger.info("HTTP服务器启动成功!")
                logger.info(f"访问地址: http://{self.config['server']['host']}:{port}")
            else:
                logger.error("HTTP服务器启动失败，请检查日志")
                
        except Exception as e:
            logger.error(f"启动服务器失败: {str(e)}")
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
            logger.info("开始简单HTTP服务器部署...")
            
            # 1. 连接SSH
            self.connect_ssh()
            
            # 2. 创建部署包
            package_name = self.create_deployment_package()
            
            # 3. 上传和解压
            self.upload_and_extract(package_name)
            
            # 4. 创建服务器脚本
            self.create_server_script()
            
            # 5. 启动服务器
            self.start_server()
            
            # 6. 健康检查
            import time
            time.sleep(5)  # 等待服务器完全启动
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
    deployer = SimpleDeploy()
    deployer.deploy()

if __name__ == '__main__':
    main() 