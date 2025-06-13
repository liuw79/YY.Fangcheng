#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Git自动化部署脚本
完整的开发到部署流程：修改代码 -> git push -> 自动部署到远程服务器
"""

import os
import sys
import json
import subprocess
import logging
import time
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('git_auto_deploy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class GitAutoDeploy:
    def __init__(self, config_path: str = 'tools/config.json'):
        """初始化Git自动部署器"""
        self.config = self._load_config(config_path)
        self.project_root = Path.cwd()

    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"配置文件未找到: {config_path}")
            sys.exit(1)

    def run_command(self, cmd: list, cwd: str = None) -> tuple:
        """运行命令并返回结果"""
        try:
            if cwd is None:
                cwd = str(self.project_root)
            
            result = subprocess.run(
                cmd, 
                cwd=cwd, 
                capture_output=True, 
                text=True, 
                check=False
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            logger.error(f"命令执行失败: {' '.join(cmd)}, 错误: {str(e)}")
            return 1, "", str(e)

    def check_git_status(self) -> bool:
        """检查Git状态"""
        logger.info("检查Git状态...")
        
        # 检查是否在Git仓库中
        returncode, stdout, stderr = self.run_command(['git', 'status'])
        if returncode != 0:
            logger.error("当前目录不是Git仓库")
            return False
        
        # 检查是否有未提交的更改
        returncode, stdout, stderr = self.run_command(['git', 'status', '--porcelain'])
        if stdout.strip():
            logger.info("发现未提交的更改:")
            print(stdout)
            return True
        else:
            logger.info("没有未提交的更改")
            return False

    def make_test_changes(self) -> bool:
        """创建测试更改"""
        try:
            # 创建或更新一个测试文件
            test_file = self.project_root / "last_deploy.txt"
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(f"最后部署时间: {timestamp}\n")
                f.write(f"部署版本: v{datetime.now().strftime('%Y%m%d_%H%M%S')}\n")
                f.write("这是一个自动部署测试文件\n")
            
            logger.info(f"创建测试更改: {test_file}")
            return True
            
        except Exception as e:
            logger.error(f"创建测试更改失败: {str(e)}")
            return False

    def git_add_commit_push(self, commit_message: str = None) -> bool:
        """Git添加、提交和推送"""
        try:
            if commit_message is None:
                commit_message = f"Auto deploy: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Git add
            logger.info("添加更改到Git...")
            returncode, stdout, stderr = self.run_command(['git', 'add', '.'])
            if returncode != 0:
                logger.error(f"Git add失败: {stderr}")
                return False
            
            # Git commit
            logger.info(f"提交更改: {commit_message}")
            returncode, stdout, stderr = self.run_command(['git', 'commit', '-m', commit_message])
            if returncode != 0:
                if "nothing to commit" in stderr:
                    logger.info("没有新的更改需要提交")
                else:
                    logger.error(f"Git commit失败: {stderr}")
                    return False
            
            # Git push
            logger.info("推送到远程仓库...")
            returncode, stdout, stderr = self.run_command(['git', 'push'])
            if returncode != 0:
                if "No configured push destination" in stderr:
                    logger.warning("没有配置远程仓库，跳过push步骤")
                else:
                    logger.error(f"Git push失败: {stderr}")
                    return False
            
            logger.info("Git操作完成")
            return True
            
        except Exception as e:
            logger.error(f"Git操作失败: {str(e)}")
            return False

    def deploy_to_server(self, use_https: bool = True) -> bool:
        """部署到服务器"""
        try:
            logger.info("开始部署到服务器...")
            
            if use_https:
                deploy_script = "tools/python_https_deploy.py"
            else:
                deploy_script = "tools/simple_deploy.py"
            
            if not os.path.exists(deploy_script):
                logger.error(f"部署脚本不存在: {deploy_script}")
                return False
            
            # 运行部署脚本
            returncode, stdout, stderr = self.run_command(['python3', deploy_script])
            
            if returncode == 0:
                logger.info("服务器部署成功")
                return True
            else:
                logger.error(f"服务器部署失败: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"服务器部署失败: {str(e)}")
            return False

    def verify_deployment(self) -> bool:
        """验证部署"""
        try:
            import requests
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # 尝试HTTPS
            https_url = f"https://{self.config['server']['domain']}:8443"
            try:
                response = requests.get(https_url, timeout=10, verify=False)
                if response.status_code == 200:
                    logger.info(f"HTTPS部署验证成功: {https_url}")
                    return True
            except:
                pass
            
            # 尝试HTTP
            http_url = f"http://{self.config['server']['domain']}:{self.config['app']['port']}"
            try:
                response = requests.get(http_url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"HTTP部署验证成功: {http_url}")
                    return True
            except:
                pass
            
            logger.warning("部署验证失败，但这可能是正常的（服务器可能需要更多时间启动）")
            return False
            
        except Exception as e:
            logger.warning(f"部署验证失败: {str(e)}")
            return False

    def update_progress(self, status: str) -> None:
        """更新进度文件"""
        try:
            progress_file = self.project_root / "progress.md"
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 读取现有内容
            existing_content = ""
            if progress_file.exists():
                with open(progress_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            
            # 添加新的部署记录
            new_entry = f"\n## 自动部署记录 - {timestamp}\n\n"
            new_entry += f"**状态**: {status}\n"
            new_entry += f"**时间**: {timestamp}\n"
            new_entry += f"**访问地址**: https://{self.config['server']['domain']}:8443\n"
            new_entry += f"**备用地址**: http://{self.config['server']['domain']}:{self.config['app']['port']}\n\n"
            
            # 写入文件
            with open(progress_file, 'w', encoding='utf-8') as f:
                f.write(existing_content + new_entry)
            
            logger.info("进度文件已更新")
            
        except Exception as e:
            logger.error(f"更新进度文件失败: {str(e)}")

    def full_workflow(self, make_changes: bool = True, use_https: bool = True) -> bool:
        """执行完整的工作流程"""
        try:
            logger.info("=" * 60)
            logger.info("开始Git自动部署工作流程")
            logger.info("=" * 60)
            
            # 1. 检查Git状态
            has_changes = self.check_git_status()
            
            # 2. 如果需要，创建测试更改
            if make_changes and not has_changes:
                if not self.make_test_changes():
                    return False
            
            # 3. Git操作
            if not self.git_add_commit_push():
                return False
            
            # 4. 等待一下，确保Git操作完成
            time.sleep(2)
            
            # 5. 部署到服务器
            if not self.deploy_to_server(use_https):
                self.update_progress("部署失败")
                return False
            
            # 6. 验证部署
            time.sleep(5)  # 等待服务器启动
            deployment_verified = self.verify_deployment()
            
            # 7. 更新进度
            status = "部署成功" if deployment_verified else "部署完成（验证失败）"
            self.update_progress(status)
            
            logger.info("=" * 60)
            logger.info("Git自动部署工作流程完成")
            logger.info(f"访问地址: https://{self.config['server']['domain']}:8443")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"工作流程失败: {str(e)}")
            self.update_progress(f"工作流程失败: {str(e)}")
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Git自动部署工具')
    parser.add_argument('--no-changes', action='store_true', help='不创建测试更改')
    parser.add_argument('--http-only', action='store_true', help='只使用HTTP部署')
    parser.add_argument('--commit-message', '-m', help='自定义提交消息')
    
    args = parser.parse_args()
    
    deployer = GitAutoDeploy()
    
    # 如果提供了自定义提交消息，先执行Git操作
    if args.commit_message:
        success = deployer.git_add_commit_push(args.commit_message)
        if success:
            success = deployer.deploy_to_server(not args.http_only)
            if success:
                deployer.verify_deployment()
                deployer.update_progress("手动部署成功")
    else:
        # 执行完整工作流程
        success = deployer.full_workflow(
            make_changes=not args.no_changes,
            use_https=not args.http_only
        )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 