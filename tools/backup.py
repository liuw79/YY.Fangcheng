#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Backup script for automated backup of application data and configuration.
Supports both local and remote backups with retention policy.
"""

import os
import sys
import json
import shutil
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import paramiko
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BackupManager:
    def __init__(self, config_path: str = 'tools/config.json'):
        """Initialize backup manager with configuration."""
        self.config = self._load_config(config_path)
        self.ssh_client = None
        self.sftp_client = None

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
            self.sftp_client = self.ssh_client.open_sftp()
            logger.info("SSH connection established successfully")
        except Exception as e:
            logger.error(f"Failed to establish SSH connection: {str(e)}")
            sys.exit(1)

    def create_backup(self, backup_type: str = 'full') -> str:
        """Create a backup of specified type."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{backup_type}_{timestamp}"
        
        try:
            # Create backup directories
            local_backup_dir = Path(self.config['backup']['local_dir'])
            local_backup_dir.mkdir(parents=True, exist_ok=True)
            
            remote_backup_dir = self.config['backup']['remote_dir']
            self.ssh_client.exec_command(f"mkdir -p {remote_backup_dir}")
            
            # Create backup package
            if backup_type == 'full':
                # Backup entire application directory
                self.ssh_client.exec_command(
                    f"tar -czf {remote_backup_dir}/{backup_name}.tar.gz -C {self.config['server']['app_dir']} ."
                )
            elif backup_type == 'data':
                # Backup only data directory
                self.ssh_client.exec_command(
                    f"tar -czf {remote_backup_dir}/{backup_name}.tar.gz -C {self.config['server']['app_dir']}/data ."
                )
            elif backup_type == 'config':
                # Backup only configuration files
                self.ssh_client.exec_command(
                    f"tar -czf {remote_backup_dir}/{backup_name}.tar.gz -C {self.config['server']['app_dir']}/config ."
                )
            
            # Download backup to local machine
            local_backup_path = local_backup_dir / f"{backup_name}.tar.gz"
            self.sftp_client.get(f"{remote_backup_dir}/{backup_name}.tar.gz", str(local_backup_path))
            
            logger.info(f"Backup created successfully: {backup_name}")
            return backup_name
            
        except Exception as e:
            logger.error(f"Backup creation failed: {str(e)}")
            sys.exit(1)

    def cleanup_old_backups(self) -> None:
        """Remove backups older than retention period."""
        try:
            retention_days = self.config['backup']['retention_days']
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # Cleanup remote backups
            remote_backup_dir = self.config['backup']['remote_dir']
            stdin, stdout, stderr = self.ssh_client.exec_command(f"ls {remote_backup_dir}")
            remote_files = stdout.read().decode().splitlines()
            
            for file in remote_files:
                if file.startswith('backup_'):
                    try:
                        file_date = datetime.strptime(file.split('_')[2], '%Y%m%d')
                        if file_date < cutoff_date:
                            self.ssh_client.exec_command(f"rm {remote_backup_dir}/{file}")
                            logger.info(f"Removed old remote backup: {file}")
                    except ValueError:
                        continue
            
            # Cleanup local backups
            local_backup_dir = Path(self.config['backup']['local_dir'])
            for file in local_backup_dir.glob('backup_*.tar.gz'):
                try:
                    file_date = datetime.strptime(file.stem.split('_')[2], '%Y%m%d')
                    if file_date < cutoff_date:
                        file.unlink()
                        logger.info(f"Removed old local backup: {file.name}")
                except ValueError:
                    continue
                    
        except Exception as e:
            logger.error(f"Backup cleanup failed: {str(e)}")
            sys.exit(1)

    def restore_backup(self, backup_name: str, restore_type: str = 'full') -> None:
        """Restore from a backup."""
        try:
            remote_backup_dir = self.config['backup']['remote_dir']
            backup_path = f"{remote_backup_dir}/{backup_name}.tar.gz"
            
            # Verify backup exists
            stdin, stdout, stderr = self.ssh_client.exec_command(f"test -f {backup_path} && echo 'exists'")
            if not stdout.read().strip():
                raise Exception(f"Backup not found: {backup_name}")
            
            # Create temporary restore directory
            temp_dir = f"{self.config['server']['temp_dir']}/restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.ssh_client.exec_command(f"mkdir -p {temp_dir}")
            
            # Extract backup
            self.ssh_client.exec_command(f"tar -xzf {backup_path} -C {temp_dir}")
            
            if restore_type == 'full':
                # Restore entire application
                self.ssh_client.exec_command(f"rsync -av --delete {temp_dir}/ {self.config['server']['app_dir']}/")
            elif restore_type == 'data':
                # Restore only data
                self.ssh_client.exec_command(f"rsync -av --delete {temp_dir}/ {self.config['server']['app_dir']}/data/")
            elif restore_type == 'config':
                # Restore only configuration
                self.ssh_client.exec_command(f"rsync -av --delete {temp_dir}/ {self.config['server']['app_dir']}/config/")
            
            # Cleanup
            self.ssh_client.exec_command(f"rm -rf {temp_dir}")
            
            logger.info(f"Successfully restored backup: {backup_name}")
            
        except Exception as e:
            logger.error(f"Backup restoration failed: {str(e)}")
            sys.exit(1)

    def list_backups(self) -> List[str]:
        """List all available backups."""
        try:
            remote_backup_dir = self.config['backup']['remote_dir']
            stdin, stdout, stderr = self.ssh_client.exec_command(f"ls {remote_backup_dir}")
            remote_files = stdout.read().decode().splitlines()
            
            local_backup_dir = Path(self.config['backup']['local_dir'])
            local_files = [f.name for f in local_backup_dir.glob('backup_*.tar.gz')]
            
            all_backups = set(remote_files + local_files)
            return sorted(list(all_backups))
            
        except Exception as e:
            logger.error(f"Failed to list backups: {str(e)}")
            return []

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.sftp_client:
            self.sftp_client.close()
        if self.ssh_client:
            self.ssh_client.close()

def main():
    parser = argparse.ArgumentParser(description='Backup Manager')
    parser.add_argument('--config', default='tools/config.json', help='Path to configuration file')
    parser.add_argument('--type', choices=['full', 'data', 'config'], default='full', help='Type of backup to create')
    parser.add_argument('--restore', help='Name of backup to restore')
    parser.add_argument('--list', action='store_true', help='List available backups')
    parser.add_argument('--cleanup', action='store_true', help='Cleanup old backups')
    args = parser.parse_args()

    manager = BackupManager(args.config)
    
    try:
        manager.connect_ssh()
        
        if args.list:
            backups = manager.list_backups()
            print("\nAvailable backups:")
            for backup in backups:
                print(f"- {backup}")
                
        elif args.restore:
            manager.restore_backup(args.restore, args.type)
            
        elif args.cleanup:
            manager.cleanup_old_backups()
            
        else:
            manager.create_backup(args.type)
            manager.cleanup_old_backups()
            
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}")
        sys.exit(1)
    finally:
        manager.cleanup()

if __name__ == '__main__':
    main() 