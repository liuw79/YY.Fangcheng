#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quick Deploy - Fast deployment with HTTPS support
"""

import os
import sys
import json
import subprocess
import logging
import paramiko
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def deploy_https_server():
    """Deploy HTTPS server to port 8888"""
    try:
        logger.info("Starting HTTPS deployment to port 8888...")
        
        # SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('op.gaowei.com', username='root', 
                   key_filename=os.path.expanduser('~/.ssh/id_rsa'))
        
        logger.info("SSH connected successfully")
        
        # Stop existing processes
        ssh.exec_command("pkill -f 'python3.*http'")
        
        # Create HTTPS server script
        https_script = '''#!/usr/bin/env python3
import http.server, ssl, socketserver, os
PORT = 8888
CERT = "/root/cert/gaowei.crt"
KEY = "/root/cert/gaowei.key"
os.chdir("/var/www/fangcheng")
httpd = socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler)
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(CERT, KEY)
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
print(f"HTTPS server on port {PORT}")
httpd.serve_forever()
'''
        
        # Upload and run script
        stdin, stdout, stderr = ssh.exec_command(f"cd /var/www/fangcheng && cat > https_server.py << 'EOF'\n{https_script}\nEOF")
        ssh.exec_command("cd /var/www/fangcheng && chmod +x https_server.py")
        ssh.exec_command("cd /var/www/fangcheng && nohup python3 https_server.py > https.log 2>&1 &")
        
        logger.info("HTTPS server deployed successfully!")
        logger.info("Access URL: https://op.gaowei.com:8888")
        
        ssh.close()
        return True
        
    except Exception as e:
        logger.error(f"HTTPS deployment failed: {e}")
        return False

if __name__ == "__main__":
    deploy_https_server() 