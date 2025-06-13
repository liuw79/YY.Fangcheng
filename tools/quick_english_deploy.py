#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quick English Deploy - One-Click Deployment
Simple deployment script with English output only
"""

import os
import sys
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def quick_deploy():
    """Quick deployment with English output"""
    try:
        logger.info("=" * 50)
        logger.info("QUICK ENGLISH DEPLOY - STARTING")
        logger.info("=" * 50)
        
        # Check if we're in the right directory
        if not Path('tools/config.json').exists():
            logger.error("Configuration file not found. Please run from project root.")
            sys.exit(1)
        
        # Update timestamp in index.html
        logger.info("Updating deployment timestamp...")
        try:
            with open('index.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            import re
            pattern = r'最后部署: \d{4}-\d{2}-\d{2} \d{2}:\d{2}'
            replacement = f'最后部署: {timestamp}'
            
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                with open('index.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Timestamp updated to: {timestamp}")
            else:
                logger.warning("Timestamp pattern not found, skipping update")
        except Exception as e:
            logger.warning(f"Failed to update timestamp: {e}")
        
        # Run Git workflow
        logger.info("Running Git auto-deploy workflow...")
        
        git_script = Path('tools/english_git_deploy.py')
        if git_script.exists():
            cmd = [sys.executable, str(git_script), '--skip-git']
            result = subprocess.run(cmd)
            
            if result.returncode == 0:
                logger.info("=" * 50)
                logger.info("QUICK DEPLOY COMPLETED SUCCESSFULLY!")
                logger.info("=" * 50)
                logger.info("Access URLs:")
                logger.info("  HTTPS: https://op.gaowei.com")
                logger.info("  HTTP:  http://op.gaowei.com:8888")
                logger.info("=" * 50)
            else:
                logger.error("Deployment failed!")
                sys.exit(1)
        else:
            logger.error("Git deploy script not found!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Quick deploy failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    quick_deploy() 