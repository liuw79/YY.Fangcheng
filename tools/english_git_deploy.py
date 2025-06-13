#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
English Git Auto-Deploy Script
Complete Git workflow + HTTPS deployment automation
Avoids encoding issues by using English output only
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('english_git_deploy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class EnglishGitDeploy:
    def __init__(self, config_path: str = 'tools/config.json'):
        """Initialize English Git Auto-Deploy"""
        self.config = self._load_config(config_path)
        self.project_root = Path.cwd()
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)

    def check_git_status(self) -> dict:
        """Check Git repository status"""
        try:
            # Check if Git repository exists
            if not (self.project_root / '.git').exists():
                logger.warning("Git repository not found, initializing...")
                subprocess.run(['git', 'init'], check=True)
                logger.info("Git repository initialized")
            
            # Get status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            
            status = {
                'has_changes': bool(result.stdout.strip()),
                'changes': result.stdout.strip().split('\n') if result.stdout.strip() else [],
                'is_git_repo': True
            }
            
            # Get current branch
            try:
                branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                             capture_output=True, text=True, check=True)
                status['current_branch'] = branch_result.stdout.strip() or 'main'
            except:
                status['current_branch'] = 'main'
            
            # Check remote
            try:
                remote_result = subprocess.run(['git', 'remote', '-v'], 
                                             capture_output=True, text=True, check=True)
                status['has_remote'] = bool(remote_result.stdout.strip())
                status['remotes'] = remote_result.stdout.strip()
            except:
                status['has_remote'] = False
                status['remotes'] = ''
            
            return status
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git status check failed: {e}")
            return {'has_changes': False, 'changes': [], 'is_git_repo': False}

    def update_deployment_timestamp(self) -> None:
        """Update deployment timestamp in index.html"""
        try:
            index_file = self.project_root / 'index.html'
            if not index_file.exists():
                logger.warning("index.html not found, skipping timestamp update")
                return
            
            # Read current content
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            
            # Replace deployment timestamp (Chinese format)
            import re
            pattern = r'最后部署: \d{4}-\d{2}-\d{2} \d{2}:\d{2}'
            replacement = f'最后部署: {timestamp}'
            
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                logger.info(f"Updated deployment timestamp to: {timestamp}")
            else:
                logger.warning("Deployment timestamp pattern not found in index.html")
            
            # Write back
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            logger.error(f"Failed to update deployment timestamp: {e}")

    def git_add_commit(self, commit_message: str = None) -> bool:
        """Add and commit changes to Git"""
        try:
            status = self.check_git_status()
            
            if not status['has_changes']:
                logger.info("No changes to commit")
                return True
            
            logger.info(f"Found {len(status['changes'])} changes to commit:")
            for change in status['changes']:
                logger.info(f"  {change}")
            
            # Add all changes
            subprocess.run(['git', 'add', '.'], check=True)
            logger.info("Added all changes to staging area")
            
            # Generate commit message if not provided
            if not commit_message:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                commit_message = f"Auto-deploy update - {timestamp}"
            
            # Commit changes
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            logger.info(f"Committed changes with message: {commit_message}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git commit failed: {e}")
            return False

    def git_push(self) -> bool:
        """Push changes to remote repository"""
        try:
            status = self.check_git_status()
            
            if not status['has_remote']:
                logger.warning("No remote repository configured, skipping push")
                return True
            
            # Push to remote
            current_branch = status['current_branch']
            try:
                subprocess.run(['git', 'push', 'origin', current_branch], check=True)
                logger.info(f"Successfully pushed to origin/{current_branch}")
                return True
            except subprocess.CalledProcessError:
                # Try to set upstream if first push
                try:
                    subprocess.run(['git', 'push', '-u', 'origin', current_branch], check=True)
                    logger.info(f"Successfully pushed and set upstream origin/{current_branch}")
                    return True
                except subprocess.CalledProcessError as e:
                    logger.error(f"Git push failed: {e}")
                    return False
                    
        except Exception as e:
            logger.error(f"Git push error: {e}")
            return False

    def run_deployment(self, https_mode: bool = True) -> bool:
        """Run the deployment script"""
        try:
            deploy_script = self.project_root / 'tools' / 'english_https_deploy.py'
            
            if not deploy_script.exists():
                logger.error("Deployment script not found: tools/english_https_deploy.py")
                return False
            
            # Build command
            cmd = [sys.executable, str(deploy_script)]
            if not https_mode:
                cmd.append('--http-only')
            
            logger.info("Starting deployment process...")
            
            # Run deployment
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Log output
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        logger.info(f"DEPLOY: {line}")
            
            if result.stderr:
                for line in result.stderr.split('\n'):
                    if line.strip():
                        logger.warning(f"DEPLOY ERROR: {line}")
            
            if result.returncode == 0:
                logger.info("Deployment completed successfully!")
                return True
            else:
                logger.error(f"Deployment failed with exit code: {result.returncode}")
                return False
                
        except Exception as e:
            logger.error(f"Deployment execution failed: {e}")
            return False

    def full_workflow(self, commit_message: str = None, https_mode: bool = True, skip_git: bool = False) -> None:
        """Execute complete Git + Deploy workflow"""
        try:
            logger.info("Starting English Git Auto-Deploy workflow...")
            
            # Step 1: Update deployment timestamp
            self.update_deployment_timestamp()
            
            if not skip_git:
                # Step 2: Git add and commit
                if not self.git_add_commit(commit_message):
                    logger.error("Git commit failed, stopping workflow")
                    return
                
                # Step 3: Git push (optional, continue even if fails)
                if not self.git_push():
                    logger.warning("Git push failed, but continuing with deployment")
            else:
                logger.info("Skipping Git operations as requested")
            
            # Step 4: Deploy
            if not self.run_deployment(https_mode):
                logger.error("Deployment failed")
                return
            
            # Step 5: Final status
            logger.info("=" * 60)
            logger.info("WORKFLOW COMPLETED SUCCESSFULLY!")
            logger.info("=" * 60)
            
            if https_mode:
                logger.info(f"HTTPS URL: https://{self.config['server']['domain']}")
                logger.info(f"HTTP URL: http://{self.config['server']['domain']}:{self.config['app']['port']}")
                logger.info("Using official DigiCert SSL certificate")
            else:
                logger.info(f"HTTP URL: http://{self.config['server']['domain']}:{self.config['app']['port']}")
            
            logger.info("Deployment workflow completed!")
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            sys.exit(1)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='English Git Auto-Deploy Tool')
    parser.add_argument('-m', '--message', help='Git commit message')
    parser.add_argument('--http-only', action='store_true', help='Deploy HTTP only (no HTTPS)')
    parser.add_argument('--skip-git', action='store_true', help='Skip Git operations, deploy only')
    
    args = parser.parse_args()
    
    deployer = EnglishGitDeploy()
    deployer.full_workflow(
        commit_message=args.message,
        https_mode=not args.http_only,
        skip_git=args.skip_git
    )

if __name__ == '__main__':
    main() 