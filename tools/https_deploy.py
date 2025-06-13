#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTTPS部署脚本 - 支持SSL证书和nginx反向代理
自动生成自签名证书或使用现有证书
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
        logging.FileHandler('https_deploy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class HTTPSDeploy:
    def __init__(self, config_path: str = 'tools/config.json'):
        """初始化HTTPS部署器"""
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
            cert_dir = "/usr/local/nginx/conf/ssl"
            
            # 创建SSL目录
            self.ssh_client.exec_command(f"mkdir -p {cert_dir}")
            
            # 生成私钥
            self.ssh_client.exec_command(f"openssl genrsa -out {cert_dir}/{domain}.key 2048")
            
            # 生成证书签名请求
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
"""
            
            # 创建临时配置文件
            with open('temp_ssl.conf', 'w') as f:
                f.write(csr_config)
            
            # 上传配置文件
            self.sftp_client.put('temp_ssl.conf', f"{cert_dir}/ssl.conf")
            os.remove('temp_ssl.conf')
            
            # 生成自签名证书
            self.ssh_client.exec_command(f"openssl req -new -x509 -key {cert_dir}/{domain}.key -out {cert_dir}/{domain}.crt -days 365 -config {cert_dir}/ssl.conf")
            
            logger.info("SSL证书创建完成")
            
        except Exception as e:
            logger.error(f"SSL证书创建失败: {str(e)}")
            sys.exit(1)

    def configure_nginx_https(self) -> None:
        """配置nginx HTTPS"""
        try:
            domain = self.config['server']['domain']
            port = self.config['app']['port']
            cert_dir = "/usr/local/nginx/conf/ssl"
            
            # 创建nginx配置
            nginx_config = f"""# HTTP重定向到HTTPS
server {{
    listen 80;
    server_name {domain};
    return 301 https://$server_name$request_uri;
}}

# HTTPS服务器
server {{
    listen 443 ssl http2;
    server_name {domain};
    
    # SSL证书配置
    ssl_certificate {cert_dir}/{domain}.crt;
    ssl_certificate_key {cert_dir}/{domain}.key;
    
    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 反向代理到应用
    location / {{
        proxy_pass http://localhost:{port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_redirect off;
    }}
    
    # 健康检查
    location /health {{
        proxy_pass http://localhost:{port}/health;
        access_log off;
    }}
    
    # 静态文件缓存
    location ~* \\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
        proxy_pass http://localhost:{port};
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    # 日志
    access_log /var/log/nginx/{self.config['app']['name']}_https_access.log;
    error_log /var/log/nginx/{self.config['app']['name']}_https_error.log;
}}"""

            # 备份原配置
            self.ssh_client.exec_command("cp /usr/local/nginx/conf/nginx.conf /usr/local/nginx/conf/nginx.conf.backup")
            
            # 读取当前nginx配置
            stdin, stdout, stderr = self.ssh_client.exec_command("cat /usr/local/nginx/conf/nginx.conf")
            current_config = stdout.read().decode()
            
            # 在http块中添加新的server配置
            if "# Fangcheng HTTPS Configuration" not in current_config:
                # 找到http块的结束位置
                http_end = current_config.rfind("}")
                if http_end != -1:
                    new_config = (current_config[:http_end] + 
                                "\n    # Fangcheng HTTPS Configuration\n" +
                                nginx_config + "\n\n" +
                                current_config[http_end:])
                    
                    # 写入新配置
                    with open('temp_nginx_full.conf', 'w') as f:
                        f.write(new_config)
                    
                    # 上传配置文件
                    self.sftp_client.put('temp_nginx_full.conf', '/usr/local/nginx/conf/nginx.conf')
                    os.remove('temp_nginx_full.conf')
                    
                    # 测试nginx配置
                    stdin, stdout, stderr = self.ssh_client.exec_command("/usr/local/nginx/sbin/nginx -t")
                    error = stderr.read().decode()
                    if "successful" not in error:
                        raise Exception(f"Nginx配置测试失败: {error}")
                    
                    # 重新加载nginx
                    self.ssh_client.exec_command("/usr/local/nginx/sbin/nginx -s reload")
                    
                    logger.info("Nginx HTTPS配置完成")
                else:
                    raise Exception("无法找到nginx配置中的http块")
            else:
                logger.info("Nginx HTTPS配置已存在，跳过")
            
        except Exception as e:
            logger.error(f"Nginx HTTPS配置失败: {str(e)}")
            # 恢复备份
            self.ssh_client.exec_command("cp /usr/local/nginx/conf/nginx.conf.backup /usr/local/nginx/conf/nginx.conf")
            sys.exit(1)

    def start_application(self) -> None:
        """启动应用"""
        try:
            app_dir = self.config['server']['app_dir']
            port = self.config['app']['port']
            
            # 停止可能存在的进程
            self.ssh_client.exec_command(f"pkill -f 'python.*server.py'")
            
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
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{{"status": "healthy", "timestamp": "' + 
                           str(datetime.now().isoformat()).encode() + b'"}}')
            return
        super().do_GET()

if __name__ == "__main__":
    from datetime import datetime
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("127.0.0.1", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Server running on port {{PORT}}")
        print(f"Access URL: https://{self.config['server']['domain']}")
        httpd.serve_forever()
"""
            
            # 写入服务器脚本
            with open('temp_https_server.py', 'w') as f:
                f.write(server_script)
            
            # 上传脚本
            self.sftp_client.put('temp_https_server.py', f"{app_dir}/server.py")
            os.remove('temp_https_server.py')
            
            # 设置执行权限
            self.ssh_client.exec_command(f"chmod +x {app_dir}/server.py")
            
            # 启动应用（后台运行）
            logger.info(f"启动应用在端口 {port}...")
            self.ssh_client.exec_command(f"cd {app_dir} && nohup python3 server.py > server.log 2>&1 &")
            
            # 等待启动
            import time
            time.sleep(3)
            
            # 检查进程是否启动
            stdin, stdout, stderr = self.ssh_client.exec_command(f"ps aux | grep 'python.*server.py' | grep -v grep")
            process = stdout.read().decode().strip()
            
            if process:
                logger.info("应用启动成功!")
                logger.info(f"HTTPS访问地址: https://{self.config['server']['domain']}")
            else:
                logger.error("应用启动失败，请检查日志")
                
        except Exception as e:
            logger.error(f"启动应用失败: {str(e)}")
            sys.exit(1)

    def health_check(self) -> bool:
        """健康检查"""
        try:
            import requests
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            url = f"https://{self.config['server']['domain']}/health"
            response = requests.get(url, timeout=10, verify=False)
            
            if response.status_code == 200:
                logger.info("HTTPS健康检查通过")
                return True
            else:
                logger.warning(f"HTTPS健康检查失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"HTTPS健康检查失败: {str(e)}")
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
            logger.info("开始HTTPS部署...")
            
            # 1. 连接SSH
            self.connect_ssh()
            
            # 2. 创建部署包
            package_name = self.create_deployment_package()
            
            # 3. 上传和解压
            self.upload_and_extract(package_name)
            
            # 4. 创建SSL证书
            self.create_ssl_certificate()
            
            # 5. 配置nginx HTTPS
            self.configure_nginx_https()
            
            # 6. 启动应用
            self.start_application()
            
            # 7. 健康检查
            import time
            time.sleep(5)  # 等待服务器完全启动
            if self.health_check():
                logger.info("HTTPS部署成功完成!")
            else:
                logger.info("HTTPS部署完成，但健康检查未通过，请手动检查")
            
            logger.info(f"HTTPS访问地址: https://{self.config['server']['domain']}")
            logger.info("注意: 使用的是自签名证书，浏览器会显示安全警告，这是正常的")
            
        except Exception as e:
            logger.error(f"HTTPS部署失败: {str(e)}")
            sys.exit(1)
        finally:
            self.cleanup()

def main():
    deployer = HTTPSDeploy()
    deployer.deploy()

if __name__ == '__main__':
    main()