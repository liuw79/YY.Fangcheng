#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Python HTTPS部署脚本 - 使用Python内置HTTPS服务器
自动生成自签名证书并启动HTTPS服务
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
        logging.FileHandler('python_https_deploy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class PythonHTTPSDeploy:
    def __init__(self, config_path: str = 'tools/config.json'):
        """初始化Python HTTPS部署器"""
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

    def create_ssl_certificate(self) -> None:
        """创建自签名SSL证书"""
        try:
            domain = self.config['server']['domain']
            app_dir = self.config['server']['app_dir']
            
            # 生成私钥
            self.ssh_client.exec_command(f"openssl genrsa -out {app_dir}/server.key 2048")
            
            # 生成证书签名请求配置
            csr_config = f"""[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = CN
ST = Beijing
L = Beijing
O = Fangcheng
OU = IT Department
CN = {domain}

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = {domain}
DNS.2 = www.{domain}
IP.1 = 127.0.0.1
"""
            
            # 创建临时配置文件
            with open('temp_ssl.conf', 'w') as f:
                f.write(csr_config)
            
            # 上传配置文件
            self.sftp_client.put('temp_ssl.conf', f"{app_dir}/ssl.conf")
            os.remove('temp_ssl.conf')
            
            # 生成自签名证书
            self.ssh_client.exec_command(f"openssl req -new -x509 -key {app_dir}/server.key -out {app_dir}/server.crt -days 365 -config {app_dir}/ssl.conf")
            
            logger.info("SSL证书创建完成")
            
        except Exception as e:
            logger.error(f"SSL证书创建失败: {str(e)}")
            sys.exit(1)

    def start_https_application(self) -> None:
        """启动HTTPS应用"""
        try:
            app_dir = self.config['server']['app_dir']
            port = self.config['app']['port']
            https_port = 8443  # HTTPS端口
            
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

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = '{{"status": "healthy", "timestamp": "' + datetime.now().isoformat() + '", "protocol": "HTTPS"}}'
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
            self.send_header('Location', f'https://{{host}}:8443{{self.path}}')
            self.end_headers()
    
    with socketserver.TCPServer(("0.0.0.0", HTTP_PORT), HTTPSRedirectHandler) as httpd:
        print(f"HTTP redirect server running on port {{HTTP_PORT}}")
        httpd.serve_forever()

def start_https_server():
    \"\"\"启动HTTPS服务器\"\"\"
    os.chdir(DIRECTORY)
    
    # 创建SSL上下文
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(f"{app_dir}/server.crt", f"{app_dir}/server.key")
    
    with socketserver.TCPServer(("0.0.0.0", HTTPS_PORT), MyHTTPRequestHandler) as httpd:
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        print(f"HTTPS server running on port {{HTTPS_PORT}}")
        print(f"Access URL: https://{self.config['server']['domain']}:{{HTTPS_PORT}}")
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
            with open('temp_https_server.py', 'w') as f:
                f.write(server_script)
            
            # 上传脚本
            self.sftp_client.put('temp_https_server.py', f"{app_dir}/https_server.py")
            os.remove('temp_https_server.py')
            
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
                logger.info(f"HTTPS访问地址: https://{self.config['server']['domain']}:{https_port}")
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
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # 检查HTTPS
            https_url = f"https://{self.config['server']['domain']}:8443/health"
            try:
                response = requests.get(https_url, timeout=10, verify=False)
                if response.status_code == 200:
                    logger.info("HTTPS健康检查通过")
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

    def cleanup(self) -> None:
        """清理资源"""
        if self.sftp_client:
            self.sftp_client.close()
        if self.ssh_client:
            self.ssh_client.close()

    def deploy(self) -> None:
        """执行完整HTTPS部署流程"""
        try:
            logger.info("开始Python HTTPS部署...")
            
            # 1. 连接SSH
            self.connect_ssh()
            
            # 2. 创建部署包
            package_name = self.create_deployment_package()
            
            # 3. 上传和解压
            self.upload_and_extract(package_name)
            
            # 4. 创建SSL证书
            self.create_ssl_certificate()
            
            # 5. 启动HTTPS应用
            self.start_https_application()
            
            # 6. 健康检查
            import time
            time.sleep(5)  # 等待服务器完全启动
            if self.health_check():
                logger.info("Python HTTPS部署成功完成!")
            else:
                logger.info("Python HTTPS部署完成，但健康检查未通过，请手动检查")
            
            logger.info(f"HTTPS访问地址: https://{self.config['server']['domain']}:8443")
            logger.info(f"HTTP重定向地址: http://{self.config['server']['domain']}:{self.config['app']['port']}")
            logger.info("注意: 使用的是自签名证书，浏览器会显示安全警告，这是正常的")
            
        except Exception as e:
            logger.error(f"Python HTTPS部署失败: {str(e)}")
            sys.exit(1)
        finally:
            self.cleanup()

def main():
    deployer = PythonHTTPSDeploy()
    deployer.deploy()

if __name__ == '__main__':
    main() 