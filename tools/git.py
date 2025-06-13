#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Git Auto Deploy - Complete Git workflow + deployment
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
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class GitDeploy:
    def __init__(self, config_path: str = 'tools/config.json'):
        """Initialize Git Auto-Deploy"""
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

    def update_timestamp(self) -> None:
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
            
            # Replace deployment timestamp
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

    def git_commit_push(self, commit_message: str = None) -> bool:
        """Add, commit and push changes to Git"""
        try:
            # Check if Git repository exists
            if not (self.project_root / '.git').exists():
                logger.warning("Git repository not found, initializing...")
                subprocess.run(['git', 'init'], check=True)
                logger.info("Git repository initialized")
            
            # Get status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                logger.info("No changes to commit")
                return True
            
            changes = result.stdout.strip().split('\n')
            logger.info(f"Found {len(changes)} changes to commit")
            
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
            
            # Push to remote (if exists)
            try:
                subprocess.run(['git', 'push'], check=True)
                logger.info("Successfully pushed to remote repository")
            except subprocess.CalledProcessError:
                try:
                    subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
                    logger.info("Successfully pushed and set upstream")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Git push failed: {e}")
                    logger.info("Continuing with deployment...")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git operations failed: {e}")
            return False

    def deploy(self) -> bool:
        """Run the deployment script"""
        try:
            deploy_script = self.project_root / 'tools' / 'deploy.py'
            
            if not deploy_script.exists():
                logger.error("Deployment script not found: tools/deploy.py")
                return False
            
            logger.info("Starting deployment process...")
            
            # Run deployment
            result = subprocess.run([sys.executable, str(deploy_script)])
            
            if result.returncode == 0:
                logger.info("Deployment completed successfully!")
                return True
            else:
                logger.error(f"Deployment failed with exit code: {result.returncode}")
                return False
                
        except Exception as e:
            logger.error(f"Deployment execution failed: {e}")
            return False

    def full_workflow(self, commit_message: str = None, skip_git: bool = False) -> None:
        """Execute complete Git + Deploy workflow"""
        try:
            logger.info("=== GIT AUTO-DEPLOY WORKFLOW STARTING ===")
            
            # Step 1: Update deployment timestamp
            self.update_timestamp()
            
            if not skip_git:
                # Step 2: Git add, commit and push
                if not self.git_commit_push(commit_message):
                    logger.error("Git operations failed, stopping workflow")
                    return
            else:
                logger.info("Skipping Git operations as requested")
            
            # Step 3: Deploy
            if not self.deploy():
                logger.error("Deployment failed")
                return
            
            # Step 4: Final status
            logger.info("=" * 50)
            logger.info("WORKFLOW COMPLETED SUCCESSFULLY!")
            logger.info("=" * 50)
            logger.info(f"HTTPS URL: https://{self.config['server']['domain']}")
            logger.info(f"HTTP URL: http://{self.config['server']['domain']}:{self.config['app']['port']}")
            logger.info("Deployment workflow completed!")
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            sys.exit(1)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Git Auto-Deploy Tool')
    parser.add_argument('-m', '--message', help='Git commit message')
    parser.add_argument('--skip-git', action='store_true', help='Skip Git operations, deploy only')
    
    args = parser.parse_args()
    
    deployer = GitDeploy()
    deployer.full_workflow(
        commit_message=args.message,
        skip_git=args.skip_git
    )

if __name__ == '__main__':
    main() 