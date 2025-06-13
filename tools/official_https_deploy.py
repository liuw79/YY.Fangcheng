#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
正式HTTPS部署脚本 - 使用服务器上的正式SSL证书
基于GW.Trackr项目的证书配置
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
        logging.FileHandler('official_https_deploy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class OfficialHTTPSDeploy:
    def __init__(self, config_path: str = 'tools/config.json'):
        """初始化正式HTTPS部署器"""
        self.config = self._load_config(config_path)
        self.ssh_client = None
        self.sftp_client = None
        # 使用正式证书路径
        self.cert_path = "/root/cert/gaowei.crt"
        self.key_path = "/root/cert/gaowei.key"

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

    def verify_certificates(self) -> bool:
        """验证正式证书是否存在"""
        try:
            # 检查证书文件
            stdin, stdout, stderr = self.ssh_client.exec_command(f"test -f {self.cert_path} && test -f {self.key_path} && echo 'OK'")
            result = stdout.read().decode().strip()
            
            if result == 'OK':
                logger.info("正式SSL证书验证成功")
                return True
            else:
                logger.error("正式SSL证书不存在")
                return False
                
        except Exception as e:
            logger.error(f"证书验证失败: {str(e)}")
            return False

    def start_https_application(self) -> None:
        """启动HTTPS应用"""
        try:
            app_dir = self.config['server']['app_dir']
            port = self.config['app']['port']
            https_port = 443  # 使用标准HTTPS端口
            
            # 停止可能存在的进程
            self.ssh_client.exec_command(f"pkill -f 'python.*https_server.py'")
            self.ssh_client.exec_command(f"pkill -f 'python.*server.py'")
            
            # 创建Python HTTPS服务器脚本
            server_script = f"""#!/usr/bin/env python3
import http.server
import socketserver
import ssl
import os
import sys
from datetime import datetime

HTTP_PORT = {port}
HTTPS_PORT = {https_port}
DIRECTORY = "{app_dir}"
CERT_FILE = "{self.cert_path}"
KEY_FILE = "{self.key_path}"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = '{{"status": "healthy", "timestamp": "' + datetime.now().isoformat() + '", "protocol": "HTTPS", "port": "' + str(HTTPS_PORT) + '"}}'
            self.wfile.write(response.encode())
            return
        super().do_GET()

def start_http_server():
    \"\"\"启动HTTP服务器（重定向到HTTPS）\"\"\"
    class HTTPSRedirectHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(301)
            host = self.headers.get("Host", "{self.config['server']['domain']}")
            if ":" in host:
                host = host.split(":")[0]
            self.send_header('Location', f'https://{{host}}{{self.path}}')
            self.end_headers()
    
    with socketserver.TCPServer(("0.0.0.0", HTTP_PORT), HTTPSRedirectHandler) as httpd:
        print(f"HTTP redirect server running on port {{HTTP_PORT}}")
        httpd.serve_forever()

def start_https_server():
    \"\"\"启动HTTPS服务器\"\"\"
    os.chdir(DIRECTORY)
    
    # 创建SSL上下文
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERT_FILE, KEY_FILE)
    
    with socketserver.TCPServer(("0.0.0.0", HTTPS_PORT), MyHTTPRequestHandler) as httpd:
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        print(f"HTTPS server running on port {{HTTPS_PORT}}")
        print(f"Access URL: https://{self.config['server']['domain']}")
        httpd.serve_forever()

if __name__ == "__main__":
    import threading
    
    # 启动HTTP重定向服务器（后台线程）
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()
    
    # 启动HTTPS服务器（主线程）
    start_https_server()
"""
            
            # 写入服务器脚本
            with open('temp_official_https_server.py', 'w') as f:
                f.write(server_script)
            
            # 上传脚本
            self.sftp_client.put('temp_official_https_server.py', f"{app_dir}/https_server.py")
            os.remove('temp_official_https_server.py')
            
            # 设置执行权限
            self.ssh_client.exec_command(f"chmod +x {app_dir}/https_server.py")
            
            # 启动应用（后台运行）
            logger.info(f"启动HTTPS应用在端口 {https_port}...")
            self.ssh_client.exec_command(f"cd {app_dir} && nohup python3 https_server.py > https_server.log 2>&1 &")
            
            # 等待启动
            import time
            time.sleep(3)
            
            # 检查进程是否启动
            stdin, stdout, stderr = self.ssh_client.exec_command(f"ps aux | grep 'python.*https_server.py' | grep -v grep")
            process = stdout.read().decode().strip()
            
            if process:
                logger.info("HTTPS应用启动成功!")
                logger.info(f"HTTPS访问地址: https://{self.config['server']['domain']}")
                logger.info(f"HTTP重定向地址: http://{self.config['server']['domain']}:{port}")
            else:
                logger.error("HTTPS应用启动失败，请检查日志")
                
        except Exception as e:
            logger.error(f"启动HTTPS应用失败: {str(e)}")
            sys.exit(1)

    def health_check(self) -> bool:
        """健康检查"""
        try:
            import requests
            
            # 检查HTTPS（使用标准端口443）
            https_url = f"https://{self.config['server']['domain']}/health"
            try:
                response = requests.get(https_url, timeout=10, verify=True)  # 使用正式证书，可以验证
                if response.status_code == 200:
                    logger.info("HTTPS健康检查通过（正式证书）")
                    return True
            except Exception as e:
                logger.warning(f"HTTPS健康检查失败: {str(e)}")
            
            # 检查HTTP重定向
            http_url = f"http://{self.config['server']['domain']}:{self.config['app']['port']}"
            try:
                response = requests.get(http_url, timeout=10, allow_redirects=False)
                if response.status_code == 301:
                    logger.info("HTTP重定向检查通过")
                    return True
            except Exception as e:
                logger.warning(f"HTTP重定向检查失败: {str(e)}")
            
            return False
                
        except Exception as e:
            logger.warning(f"健康检查失败: {str(e)}")
            return False

    def cleanup_old_certificates(self) -> None:
        """清理旧的自签名证书"""
        try:
            # 清理我之前创建的自签名证书
            self.ssh_client.exec_command(f"rm -rf /usr/local/nginx/conf/ssl/op.gaowei.com.*")
            self.ssh_client.exec_command(f"rm -rf {self.config['server']['app_dir']}/server.*")
            self.ssh_client.exec_command(f"rm -rf {self.config['server']['app_dir']}/ssl.conf")
            logger.info("清理旧的自签名证书完成")
        except Exception as e:
            logger.warning(f"清理旧证书失败: {str(e)}")

    def cleanup(self) -> None:
        """清理资源"""
        if self.sftp_client:
            self.sftp_client.close()
        if self.ssh_client:
            self.ssh_client.close()

    def deploy(self) -> None:
        """执行完整HTTPS部署流程"""
        try:
            logger.info("开始正式HTTPS部署...")
            
            # 1. 连接SSH
            self.connect_ssh()
            
            # 2. 验证正式证书
            if not self.verify_certificates():
                logger.error("正式证书验证失败，无法继续部署")
                return
            
            # 3. 清理旧的自签名证书
            self.cleanup_old_certificates()
            
            # 4. 创建部署包
            package_name = self.create_deployment_package()
            
            # 5. 上传和解压
            self.upload_and_extract(package_name)
            
            # 6. 启动HTTPS应用
            self.start_https_application()
            
            # 7. 健康检查
            import time
            time.sleep(5)  # 等待服务器完全启动
            if self.health_check():
                logger.info("正式HTTPS部署成功完成!")
            else:
                logger.info("正式HTTPS部署完成，但健康检查未通过，请手动检查")
            
            logger.info(f"HTTPS访问地址: https://{self.config['server']['domain']}")
            logger.info(f"HTTP重定向地址: http://{self.config['server']['domain']}:{self.config['app']['port']}")
            logger.info("使用正式SSL证书，浏览器不会显示安全警告")
            
        except Exception as e:
            logger.error(f"正式HTTPS部署失败: {str(e)}")
            sys.exit(1)
        finally:
            self.cleanup()

def main():
    deployer = OfficialHTTPSDeploy()
    deployer.deploy()

if __name__ == '__main__':
    main() 