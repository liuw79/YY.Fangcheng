# Automated Deployment Tools

This directory contains a comprehensive set of tools for automating the deployment, backup, monitoring, and release management of your application.

## Prerequisites

1. Python 3.8 or higher
2. SSH access to your server
3. GitHub account with repository access
4. Nginx installed on the server (for reverse proxy)

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   export GITHUB_TOKEN=your_github_token
   ```

3. Configure the deployment settings in `config.json`:
   ```json
   {
       "server": {
           "host": "your-server-host",
           "username": "your-username",
           "key_path": "~/.ssh/id_rsa",
           "app_dir": "/var/www/your-app",
           "temp_dir": "/tmp",
           "domain": "your-domain.com"
       },
       "backup": {
           "remote_dir": "/var/backups/your-app",
           "local_dir": "./backups",
           "retention_days": 7
       },
       "github": {
           "repo": "your-username/your-repo",
           "branch": "main"
       },
       "app": {
           "name": "your-app-name",
           "port_range": {
               "start": 8002,
               "end": 8999
           }
       }
   }
   ```

## Available Tools

### 1. Deployment Script (`deploy.py`)

Handles the complete deployment process:
- SSH connection to server
- Port availability check
- Application deployment
- Nginx configuration
- Health checks

Usage:
```bash
python deploy.py [--config CONFIG_FILE]
```

### 2. Backup Script (`backup.py`)

Manages application backups:
- Full application backup
- Data-only backup
- Configuration backup
- Backup rotation
- Restore functionality

Usage:
```bash
python backup.py [--config CONFIG_FILE] [--type {full,data,config}] [--restore BACKUP_NAME] [--list] [--cleanup]
```

### 3. Health Check Script (`health_check.py`)

Monitors application health:
- HTTP endpoint checks
- Process monitoring
- Resource usage tracking
- Log analysis
- Automatic restart on failure

Usage:
```bash
python health_check.py [--config CONFIG_FILE] [--auto-restart] [--continuous] [--interval SECONDS]
```

### 4. GitHub Automation (`github_automation.py`)

Manages GitHub releases and changelogs:
- Version bumping
- Changelog generation
- Release creation
- Tag management

Usage:
```bash
python github_automation.py [--config CONFIG_FILE] [--bump {major,minor,patch}] [--skip-push] [--skip-release]
```

## Directory Structure

```
tools/
├── README.md
├── requirements.txt
├── config.json
├── deploy.py
├── backup.py
├── health_check.py
└── github_automation.py
```

## Best Practices

1. **Configuration**
   - Keep sensitive information in environment variables
   - Use SSH keys for authentication
   - Regularly update the configuration file

2. **Backup**
   - Schedule regular backups
   - Test restore procedures
   - Monitor backup storage usage

3. **Deployment**
   - Always run health checks after deployment
   - Use version control for all changes
   - Keep deployment logs

4. **Monitoring**
   - Set up continuous health checks
   - Configure alerts for critical issues
   - Monitor resource usage

## Security Considerations

1. **Access Control**
   - Use SSH keys instead of passwords
   - Limit server access to necessary users
   - Regularly rotate credentials

2. **Data Protection**
   - Encrypt sensitive data
   - Secure backup storage
   - Implement proper file permissions

3. **Network Security**
   - Use HTTPS for all connections
   - Configure firewall rules
   - Monitor for suspicious activity

## Troubleshooting

1. **Deployment Issues**
   - Check SSH connectivity
   - Verify port availability
   - Review application logs

2. **Backup Problems**
   - Check disk space
   - Verify backup permissions
   - Test restore procedures

3. **Health Check Failures**
   - Review application logs
   - Check resource usage
   - Verify network connectivity

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 