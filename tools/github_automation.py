#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub automation script for managing releases, changelogs, and tags.
Supports automatic version bumping, changelog generation, and release creation.
"""

import os
import sys
import json
import logging
import argparse
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
from github import Github
from github.GithubException import GithubException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('github_automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class GitHubAutomation:
    def __init__(self, config_path: str = 'tools/config.json'):
        """Initialize GitHub automation with configuration."""
        self.config = self._load_config(config_path)
        self.github_client = None
        self.repo = None

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

    def connect_github(self) -> None:
        """Connect to GitHub using token."""
        try:
            token = os.getenv('GITHUB_TOKEN')
            if not token:
                raise ValueError("GITHUB_TOKEN environment variable not set")
            
            self.github_client = Github(token)
            self.repo = self.github_client.get_repo(self.config['github']['repo'])
            logger.info("GitHub connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to GitHub: {str(e)}")
            sys.exit(1)

    def get_current_version(self) -> str:
        """Get current version from package.json or git tags."""
        try:
            # Try to get version from package.json
            with open('package.json', 'r') as f:
                return json.load(f)['version']
        except:
            # Fallback to latest git tag
            result = subprocess.run(
                ['git', 'describe', '--tags', '--abbrev=0'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip().lstrip('v')
            return '0.0.0'

    def bump_version(self, bump_type: str = 'patch') -> str:
        """Bump version number according to semantic versioning."""
        current_version = self.get_current_version()
        major, minor, patch = map(int, current_version.split('.'))
        
        if bump_type == 'major':
            new_version = f"{major + 1}.0.0"
        elif bump_type == 'minor':
            new_version = f"{major}.{minor + 1}.0"
        else:  # patch
            new_version = f"{major}.{minor}.{patch + 1}"
            
        # Update version in package.json
        try:
            with open('package.json', 'r') as f:
                package_data = json.load(f)
            package_data['version'] = new_version
            with open('package.json', 'w') as f:
                json.dump(package_data, f, indent=2)
        except:
            logger.warning("Failed to update version in package.json")
            
        return new_version

    def generate_changelog(self, new_version: str) -> str:
        """Generate changelog from git commits since last tag."""
        try:
            # Get commits since last tag
            result = subprocess.run(
                ['git', 'log', '--pretty=format:%s', f"v{self.get_current_version()}..HEAD"],
                capture_output=True,
                text=True
            )
            commits = result.stdout.splitlines()
            
            # Generate changelog
            changelog = f"## Version {new_version} ({datetime.now().strftime('%Y-%m-%d')})\n\n"
            changelog += "### Changes\n\n"
            
            for commit in commits:
                changelog += f"- {commit}\n"
                
            # Update CHANGELOG.md
            try:
                with open('CHANGELOG.md', 'r') as f:
                    existing_changelog = f.read()
            except FileNotFoundError:
                existing_changelog = "# Changelog\n\n"
                
            with open('CHANGELOG.md', 'w') as f:
                f.write(changelog + "\n" + existing_changelog)
                
            return changelog
            
        except Exception as e:
            logger.error(f"Failed to generate changelog: {str(e)}")
            return ""

    def create_release(self, version: str, changelog: str) -> bool:
        """Create GitHub release with tag and changelog."""
        try:
            # Create git tag
            subprocess.run(['git', 'tag', '-a', f"v{version}", '-m', f"Release version {version}"])
            subprocess.run(['git', 'push', 'origin', f"v{version}"])
            
            # Create GitHub release
            self.repo.create_git_release(
                tag=f"v{version}",
                name=f"Version {version}",
                message=changelog,
                draft=False,
                prerelease=False
            )
            
            logger.info(f"Successfully created release for version {version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create release: {str(e)}")
            return False

    def push_changes(self, version: str) -> bool:
        """Push changes to GitHub repository."""
        try:
            # Add all changes
            subprocess.run(['git', 'add', '.'])
            
            # Commit changes
            subprocess.run(['git', 'commit', '-m', f"Bump version to {version}"])
            
            # Push changes
            subprocess.run(['git', 'push', 'origin', self.config['github']['branch']])
            
            logger.info("Successfully pushed changes to GitHub")
            return True
            
        except Exception as e:
            logger.error(f"Failed to push changes: {str(e)}")
            return False

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.github_client:
            self.github_client.close()

def main():
    parser = argparse.ArgumentParser(description='GitHub Automation')
    parser.add_argument('--config', default='tools/config.json', help='Path to configuration file')
    parser.add_argument('--bump', choices=['major', 'minor', 'patch'], default='patch',
                      help='Version bump type (default: patch)')
    parser.add_argument('--skip-push', action='store_true', help='Skip pushing changes to GitHub')
    parser.add_argument('--skip-release', action='store_true', help='Skip creating GitHub release')
    args = parser.parse_args()

    automation = GitHubAutomation(args.config)
    
    try:
        automation.connect_github()
        
        # Bump version
        new_version = automation.bump_version(args.bump)
        logger.info(f"Bumped version to {new_version}")
        
        # Generate changelog
        changelog = automation.generate_changelog(new_version)
        logger.info("Generated changelog")
        
        if not args.skip_push:
            # Push changes
            if automation.push_changes(new_version):
                logger.info("Changes pushed successfully")
            else:
                logger.error("Failed to push changes")
                sys.exit(1)
                
        if not args.skip_release:
            # Create release
            if automation.create_release(new_version, changelog):
                logger.info("Release created successfully")
            else:
                logger.error("Failed to create release")
                sys.exit(1)
                
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}")
        sys.exit(1)
    finally:
        automation.cleanup()

if __name__ == '__main__':
    main() 