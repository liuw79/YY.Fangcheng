#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Stable Deploy - Using Nginx + Backend HTTP Server (Like 5001 site)
"""

import os
import sys
import logging
import paramiko

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def deploy_stable_https():
    """Deploy stable HTTPS using nginx + backend server"""
    try:
        logger.info("Starting stable nginx HTTPS deployment...")
        
        # SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('op.gaowei.com', username='root', 
                   key_filename=os.path.expanduser('~/.ssh/id_rsa'))
        
        logger.info("SSH connected successfully")
        
        # Step 1: Stop old unstable python https servers
        ssh.exec_command("pkill -f 'python3.*https_server'")
        logger.info("Stopped old unstable python HTTPS servers")
        
        # Step 2: Start stable HTTP backend server (port 9000)
        stdin, stdout, stderr = ssh.exec_command("cd /var/www/fangcheng && pkill -f 'python3.*http.server.*9000' || true")
        stdin, stdout, stderr = ssh.exec_command("cd /var/www/fangcheng && nohup python3 -m http.server 9000 > backend.log 2>&1 & echo $!")
        backend_pid = stdout.read().decode().strip()
        logger.info(f"Started HTTP backend server on port 9000 (PID: {backend_pid})")
        
        # Step 3: Create nginx server block for port 8888
        nginx_config = '''
    server {
        listen 8888 ssl;
        server_name op.gaowei.com;
        
        ssl_certificate /root/cert/gaowei.crt;
        ssl_certificate_key /root/cert/gaowei.key;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;
        
        location / {
            proxy_pass http://localhost:9000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 600s;
        }
        
        access_log /var/log/nginx/fangcheng_8888.log;
        error_log /var/log/nginx/fangcheng_8888_error.log;
    }
'''
        
        # Step 4: Add server block to nginx config
        stdin, stdout, stderr = ssh.exec_command(f"""
        # Backup original config
        cp /usr/local/nginx/conf/nginx.conf /usr/local/nginx/conf/nginx.conf.backup
        
        # Remove old 8888 server block if exists
        sed -i '/# Fangcheng 8888 server/,/# End Fangcheng 8888/d' /usr/local/nginx/conf/nginx.conf
        
        # Add new server block before the last closing brace
        sed -i '$i\\    # Fangcheng 8888 server' /usr/local/nginx/conf/nginx.conf
        sed -i '$i\\{nginx_config}' /usr/local/nginx/conf/nginx.conf
        sed -i '$i\\    # End Fangcheng 8888' /usr/local/nginx/conf/nginx.conf
        """)
        
        logger.info("Added nginx server block for port 8888")
        
        # Step 5: Test and reload nginx
        stdin, stdout, stderr = ssh.exec_command("/usr/local/nginx/sbin/nginx -t")
        test_result = stdout.read().decode() + stderr.read().decode()
        
        if "syntax is ok" in test_result and "test is successful" in test_result:
            logger.info("Nginx configuration test passed")
            
            # Reload nginx
            stdin, stdout, stderr = ssh.exec_command("/usr/local/nginx/sbin/nginx -s reload")
            logger.info("Nginx reloaded successfully")
            
            # Step 6: Verify services
            import time
            time.sleep(3)
            
            # Check backend
            stdin, stdout, stderr = ssh.exec_command("netstat -tlnp | grep :9000")
            if stdout.read().strip():
                logger.info("✅ Backend HTTP server (9000) is running")
            else:
                logger.warning("⚠️ Backend HTTP server (9000) not detected")
            
            # Check nginx
            stdin, stdout, stderr = ssh.exec_command("netstat -tlnp | grep :8888")
            if stdout.read().strip():
                logger.info("✅ Nginx HTTPS proxy (8888) is running")
            else:
                logger.warning("⚠️ Nginx HTTPS proxy (8888) not detected")
            
            logger.info("🎉 Stable HTTPS deployment completed!")
            logger.info("Access URL: https://op.gaowei.com:8888")
            logger.info("Architecture: Nginx (HTTPS:8888) -> Backend (HTTP:9000)")
            
        else:
            logger.error(f"Nginx configuration test failed: {test_result}")
            return False
        
        ssh.close()
        return True
        
    except Exception as e:
        logger.error(f"Stable deployment failed: {e}")
        return False

if __name__ == "__main__":
    deploy_stable_https() 