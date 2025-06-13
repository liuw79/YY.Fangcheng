#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Health check script for monitoring application health and performance.
Supports HTTP checks, process monitoring, and resource usage tracking.
"""

import os
import sys
import json
import time
import logging
import argparse
import requests
import psutil
import paramiko
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('health_check.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class HealthChecker:
    def __init__(self, config_path: str = 'tools/config.json'):
        """Initialize health checker with configuration."""
        self.config = self._load_config(config_path)
        self.ssh_client = None

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in configuration file: {config_path}")
            sys.exit(1)

    def connect_ssh(self) -> None:
        """Establish SSH connection to the server."""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                hostname=self.config['server']['host'],
                username=self.config['server']['username'],
                key_filename=self.config['server']['key_path']
            )
            logger.info("SSH connection established successfully")
        except Exception as e:
            logger.error(f"Failed to establish SSH connection: {str(e)}")
            sys.exit(1)

    def check_http_health(self) -> Tuple[bool, str]:
        """Check HTTP health of the application."""
        try:
            response = requests.get(
                f"http://{self.config['server']['domain']}/health",
                timeout=5
            )
            if response.status_code == 200:
                return True, "HTTP health check passed"
            else:
                return False, f"HTTP health check failed with status {response.status_code}"
        except requests.RequestException as e:
            return False, f"HTTP health check failed: {str(e)}"

    def check_process_health(self) -> Tuple[bool, str]:
        """Check if the application process is running."""
        try:
            # Get process list
            stdin, stdout, stderr = self.ssh_client.exec_command(
                f"ps aux | grep {self.config['app']['name']} | grep -v grep"
            )
            processes = stdout.read().decode().strip()
            
            if processes:
                return True, "Process is running"
            else:
                return False, "Process is not running"
        except Exception as e:
            return False, f"Process check failed: {str(e)}"

    def check_resource_usage(self) -> Tuple[bool, str]:
        """Check server resource usage."""
        try:
            # Get CPU and memory usage
            stdin, stdout, stderr = self.ssh_client.exec_command(
                "top -bn1 | grep 'Cpu(s)' | awk '{print $2}'"
            )
            cpu_usage = float(stdout.read().decode().strip())
            
            stdin, stdout, stderr = self.ssh_client.exec_command(
                "free | grep Mem | awk '{print $3/$2 * 100.0}'"
            )
            memory_usage = float(stdout.read().decode().strip())
            
            # Get disk usage
            stdin, stdout, stderr = self.ssh_client.exec_command(
                f"df -h {self.config['server']['app_dir']} | tail -1 | awk '{{print $5}}'"
            )
            disk_usage = float(stdout.read().decode().strip().rstrip('%'))
            
            # Check if any resource usage is too high
            if cpu_usage > 90 or memory_usage > 90 or disk_usage > 90:
                return False, f"High resource usage detected - CPU: {cpu_usage}%, Memory: {memory_usage}%, Disk: {disk_usage}%"
            else:
                return True, f"Resource usage normal - CPU: {cpu_usage}%, Memory: {memory_usage}%, Disk: {disk_usage}%"
                
        except Exception as e:
            return False, f"Resource check failed: {str(e)}"

    def check_log_health(self) -> Tuple[bool, str]:
        """Check application logs for errors."""
        try:
            # Get recent error logs
            stdin, stdout, stderr = self.ssh_client.exec_command(
                f"tail -n 100 {self.config['server']['app_dir']}/logs/app.log | grep -i 'error\|exception\|fail'"
            )
            errors = stdout.read().decode().strip()
            
            if errors:
                return False, f"Found errors in logs:\n{errors}"
            else:
                return True, "No recent errors found in logs"
                
        except Exception as e:
            return False, f"Log check failed: {str(e)}"

    def restart_application(self) -> Tuple[bool, str]:
        """Restart the application if health checks fail."""
        try:
            # Stop the application
            self.ssh_client.exec_command(
                f"cd {self.config['server']['app_dir']} && ./stop.sh"
            )
            time.sleep(5)  # Wait for process to stop
            
            # Start the application
            self.ssh_client.exec_command(
                f"cd {self.config['server']['app_dir']} && ./start.sh"
            )
            time.sleep(10)  # Wait for process to start
            
            # Verify restart
            if self.check_process_health()[0]:
                return True, "Application restarted successfully"
            else:
                return False, "Application failed to restart"
                
        except Exception as e:
            return False, f"Restart failed: {str(e)}"

    def run_health_checks(self, auto_restart: bool = False) -> Dict[str, Tuple[bool, str]]:
        """Run all health checks and optionally restart if needed."""
        results = {
            'http': self.check_http_health(),
            'process': self.check_process_health(),
            'resources': self.check_resource_usage(),
            'logs': self.check_log_health()
        }
        
        # Check if any checks failed
        failed_checks = [check for check, (status, _) in results.items() if not status]
        
        if failed_checks and auto_restart:
            logger.warning(f"Health checks failed: {', '.join(failed_checks)}. Attempting restart...")
            restart_success, restart_message = self.restart_application()
            results['restart'] = (restart_success, restart_message)
            
            if restart_success:
                # Run checks again after restart
                results.update({
                    'http': self.check_http_health(),
                    'process': self.check_process_health(),
                    'resources': self.check_resource_usage(),
                    'logs': self.check_log_health()
                })
        
        return results

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.ssh_client:
            self.ssh_client.close()

def main():
    parser = argparse.ArgumentParser(description='Health Check Manager')
    parser.add_argument('--config', default='tools/config.json', help='Path to configuration file')
    parser.add_argument('--auto-restart', action='store_true', help='Automatically restart on failure')
    parser.add_argument('--continuous', action='store_true', help='Run checks continuously')
    parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds (default: 300)')
    args = parser.parse_args()

    checker = HealthChecker(args.config)
    
    try:
        checker.connect_ssh()
        
        if args.continuous:
            logger.info(f"Starting continuous health checks (interval: {args.interval}s)")
            while True:
                results = checker.run_health_checks(args.auto_restart)
                for check, (status, message) in results.items():
                    logger.info(f"{check.upper()}: {'PASS' if status else 'FAIL'} - {message}")
                time.sleep(args.interval)
        else:
            results = checker.run_health_checks(args.auto_restart)
            for check, (status, message) in results.items():
                logger.info(f"{check.upper()}: {'PASS' if status else 'FAIL'} - {message}")
                
    except KeyboardInterrupt:
        logger.info("Health check interrupted by user")
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        sys.exit(1)
    finally:
        checker.cleanup()

if __name__ == '__main__':
    main() 