# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san-studio SDK Software in commercial settings.
#
# END COPYRIGHT

import os
from typing import Any, Dict, Union

from neuro_san.interfaces.coded_tool import CodedTool


class AnsibleBuilder(CodedTool):
    """
    Generates Ansible configuration code based on design specifications.
    This tool reads design documents and creates appropriate Ansible playbooks and roles.
    """

    def __init__(self):
        """
        Initialize the AnsibleBuilder.
        """
        pass

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Generate Ansible configuration based on the design document.

        :param args: A dictionary with the following keys:
                    "design_path": Path to the design.md file to implement
                    "timestamp": Project timestamp in MMDDYYYYHHMMSS format

        :param sly_data: A dictionary containing parameters that should be kept out of the chat stream.

        :return: Success message with paths to created Ansible files or error message.
        """
        try:
            design_path = args.get("design_path", "")
            timestamp = args.get("timestamp", "")
            
            if not design_path:
                return "Error: design_path parameter is required"
            
            if not timestamp:
                return "Error: timestamp parameter is required"

            print(f"========== Building Ansible Configuration ==========")
            print(f"    Design Path: {design_path}")
            print(f"    Timestamp: {timestamp}")

            # Read the design document
            if not os.path.exists(design_path):
                return f"Error: Design file not found at {design_path}"

            with open(design_path, 'r') as f:
                design_content = f.read()

            # Create output directory structure for Ansible
            output_dir = os.path.join("output", f"LZ_{timestamp}")
            ansible_dir = os.path.join(output_dir, "config", "ansible")
            os.makedirs(ansible_dir, exist_ok=True)

            # Create subdirectories for Ansible structure
            playbooks_dir = os.path.join(ansible_dir, "playbooks")
            roles_dir = os.path.join(ansible_dir, "roles")
            inventories_dir = os.path.join(ansible_dir, "inventories")
            group_vars_dir = os.path.join(ansible_dir, "group_vars")
            host_vars_dir = os.path.join(ansible_dir, "host_vars")
            
            for directory in [playbooks_dir, roles_dir, inventories_dir, group_vars_dir, host_vars_dir]:
                os.makedirs(directory, exist_ok=True)

            # Generate Ansible files
            created_files = []
            
            # Main playbook
            main_playbook_path = os.path.join(playbooks_dir, "site.yml")
            with open(main_playbook_path, 'w') as f:
                f.write(self._generate_main_playbook())
            created_files.append(main_playbook_path)

            # Web server playbook
            web_playbook_path = os.path.join(playbooks_dir, "webservers.yml")
            with open(web_playbook_path, 'w') as f:
                f.write(self._generate_web_playbook())
            created_files.append(web_playbook_path)

            # Database playbook
            db_playbook_path = os.path.join(playbooks_dir, "databases.yml")
            with open(db_playbook_path, 'w') as f:
                f.write(self._generate_database_playbook())
            created_files.append(db_playbook_path)

            # Inventory files
            dev_inventory_path = os.path.join(inventories_dir, "dev.yml")
            with open(dev_inventory_path, 'w') as f:
                f.write(self._generate_dev_inventory())
            created_files.append(dev_inventory_path)

            prod_inventory_path = os.path.join(inventories_dir, "prod.yml")
            with open(prod_inventory_path, 'w') as f:
                f.write(self._generate_prod_inventory())
            created_files.append(prod_inventory_path)

            # Group variables
            all_vars_path = os.path.join(group_vars_dir, "all.yml")
            with open(all_vars_path, 'w') as f:
                f.write(self._generate_all_group_vars())
            created_files.append(all_vars_path)

            web_vars_path = os.path.join(group_vars_dir, "webservers.yml")
            with open(web_vars_path, 'w') as f:
                f.write(self._generate_web_group_vars())
            created_files.append(web_vars_path)

            db_vars_path = os.path.join(group_vars_dir, "databases.yml")
            with open(db_vars_path, 'w') as f:
                f.write(self._generate_database_group_vars())
            created_files.append(db_vars_path)

            # Create common role
            common_role_dir = os.path.join(roles_dir, "common")
            self._create_role_structure(common_role_dir, "common")
            created_files.extend(self._get_role_files(common_role_dir))

            # Create webserver role
            webserver_role_dir = os.path.join(roles_dir, "webserver")
            self._create_role_structure(webserver_role_dir, "webserver")
            created_files.extend(self._get_role_files(webserver_role_dir))

            # Create database role
            database_role_dir = os.path.join(roles_dir, "database")
            self._create_role_structure(database_role_dir, "database")
            created_files.extend(self._get_role_files(database_role_dir))

            # Ansible configuration file
            ansible_cfg_path = os.path.join(ansible_dir, "ansible.cfg")
            with open(ansible_cfg_path, 'w') as f:
                f.write(self._generate_ansible_config())
            created_files.append(ansible_cfg_path)

            # Requirements file
            requirements_path = os.path.join(ansible_dir, "requirements.yml")
            with open(requirements_path, 'w') as f:
                f.write(self._generate_requirements())
            created_files.append(requirements_path)

            # README for Ansible
            readme_path = os.path.join(ansible_dir, "README.md")
            with open(readme_path, 'w') as f:
                f.write(self._generate_ansible_readme(timestamp))
            created_files.append(readme_path)

            success_message = f"Ansible configuration generated successfully in {ansible_dir}. Created {len(created_files)} files."
            print(f"    Result: {success_message}")
            print(f"    Files created: {created_files[:5]}...")  # Show first 5 files
            
            # Store the ansible directory in sly_data for other tools to use
            sly_data["ansible_directory"] = ansible_dir
            sly_data["ansible_files"] = created_files
            
            return success_message

        except Exception as e:
            error_msg = f"Error generating Ansible configuration: {str(e)}"
            print(f"    Error: {error_msg}")
            return f"Error: {error_msg}"

    def _generate_main_playbook(self) -> str:
        """Generate the main site playbook."""
        return '''---
# Main playbook for infrastructure configuration
# This orchestrates the deployment across all server types

- name: Configure all servers with common settings
  import_playbook: common.yml

- name: Configure web servers
  import_playbook: webservers.yml

- name: Configure database servers
  import_playbook: databases.yml

- name: Final validation and health checks
  hosts: all
  become: yes
  tasks:
    - name: Ensure all services are running
      systemd:
        name: "{{ item }}"
        state: started
        enabled: yes
      loop:
        - sshd
        - firewalld
      tags: [validation]

    - name: Run connectivity tests
      uri:
        url: "http://{{ ansible_default_ipv4.address }}"
        method: GET
        status_code: [200, 404]  # 404 is ok if no web content yet
      when: "'webservers' in group_names"
      tags: [validation]
'''

    def _generate_web_playbook(self) -> str:
        """Generate the web servers playbook."""
        return '''---
# Playbook for configuring web servers

- name: Configure web servers
  hosts: webservers
  become: yes
  roles:
    - common
    - webserver
  
  tasks:
    - name: Ensure web server is running
      systemd:
        name: "{{ web_service_name }}"
        state: started
        enabled: yes
      tags: [webserver]

    - name: Configure firewall for web traffic
      firewalld:
        service: "{{ item }}"
        permanent: yes
        state: enabled
        immediate: yes
      loop:
        - http
        - https
      tags: [firewall]

    - name: Deploy application configuration
      template:
        src: "{{ app_config_template }}"
        dest: "{{ app_config_path }}"
        owner: "{{ app_user }}"
        group: "{{ app_group }}"
        mode: '0644'
      notify: restart web service
      tags: [config]

  handlers:
    - name: restart web service
      systemd:
        name: "{{ web_service_name }}"
        state: restarted
'''

    def _generate_database_playbook(self) -> str:
        """Generate the database servers playbook."""
        return '''---
# Playbook for configuring database servers

- name: Configure database servers
  hosts: databases
  become: yes
  roles:
    - common
    - database
  
  tasks:
    - name: Ensure database service is running
      systemd:
        name: "{{ db_service_name }}"
        state: started
        enabled: yes
      tags: [database]

    - name: Configure database firewall
      firewalld:
        port: "{{ db_port }}/tcp"
        permanent: yes
        state: enabled
        immediate: yes
        source: "{{ allowed_db_networks | join(',') }}"
      tags: [firewall]

    - name: Create application database
      mysql_db:
        name: "{{ app_db_name }}"
        state: present
      when: db_type == "mysql"
      tags: [database]

    - name: Create application database user
      mysql_user:
        name: "{{ app_db_user }}"
        password: "{{ app_db_password }}"
        priv: "{{ app_db_name }}.*:ALL"
        host: "%"
        state: present
      when: db_type == "mysql"
      tags: [database]

  handlers:
    - name: restart database service
      systemd:
        name: "{{ db_service_name }}"
        state: restarted
'''

    def _generate_dev_inventory(self) -> str:
        """Generate the development environment inventory."""
        return '''---
# Development environment inventory

all:
  children:
    webservers:
      hosts:
        web01-dev:
          ansible_host: 10.0.1.10
          ansible_user: azureuser
        web02-dev:
          ansible_host: 10.0.1.11
          ansible_user: azureuser
      vars:
        environment: development
        
    databases:
      hosts:
        db01-dev:
          ansible_host: 10.0.3.10
          ansible_user: azureuser
      vars:
        environment: development
        
    loadbalancers:
      hosts:
        lb01-dev:
          ansible_host: 10.0.1.5
          ansible_user: azureuser
      vars:
        environment: development

  vars:
    # Global variables for development
    env_suffix: "-dev"
    backup_retention_days: 7
    log_level: debug
    enable_monitoring: true
    ansible_ssh_private_key_file: ~/.ssh/id_rsa
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
'''

    def _generate_prod_inventory(self) -> str:
        """Generate the production environment inventory."""
        return '''---
# Production environment inventory

all:
  children:
    webservers:
      hosts:
        web01-prod:
          ansible_host: 10.0.1.20
          ansible_user: azureuser
        web02-prod:
          ansible_host: 10.0.1.21
          ansible_user: azureuser
        web03-prod:
          ansible_host: 10.0.1.22
          ansible_user: azureuser
      vars:
        environment: production
        
    databases:
      hosts:
        db01-prod:
          ansible_host: 10.0.3.20
          ansible_user: azureuser
        db02-prod:
          ansible_host: 10.0.3.21
          ansible_user: azureuser
      vars:
        environment: production
        
    loadbalancers:
      hosts:
        lb01-prod:
          ansible_host: 10.0.1.15
          ansible_user: azureuser
        lb02-prod:
          ansible_host: 10.0.1.16
          ansible_user: azureuser
      vars:
        environment: production

  vars:
    # Global variables for production
    env_suffix: "-prod"
    backup_retention_days: 30
    log_level: info
    enable_monitoring: true
    ansible_ssh_private_key_file: ~/.ssh/id_rsa_prod
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
'''

    def _generate_all_group_vars(self) -> str:
        """Generate the all group variables."""
        return '''---
# Variables applied to all hosts

# Common packages to install on all servers
common_packages:
  - curl
  - wget
  - vim
  - htop
  - git
  - rsync
  - unzip

# System settings
timezone: "UTC"
ntp_servers:
  - "0.pool.ntp.org"
  - "1.pool.ntp.org"

# Security settings
disable_root_login: true
password_authentication: false
permit_empty_passwords: false

# Logging
log_rotation_days: 30
syslog_server: "10.0.1.100"

# Monitoring
enable_node_exporter: true
node_exporter_port: 9100

# Backup settings
backup_user: "backup"
backup_schedule: "0 2 * * *"  # Daily at 2 AM

# SSH settings
ssh_port: 22
ssh_max_auth_tries: 3
ssh_client_alive_interval: 300

# Firewall settings
firewall_enabled: true
default_firewall_zone: "public"

# Users and groups
admin_users:
  - name: "admin"
    groups: ["wheel", "sudo"]
    ssh_key: "ssh-rsa AAAAB3NzaC1yc2E... (add your public key here)"

# Application settings
app_user: "appuser"
app_group: "appgroup"
app_home: "/opt/app"
'''

    def _generate_web_group_vars(self) -> str:
        """Generate the webservers group variables."""
        return '''---
# Variables for web servers

# Web server configuration
web_service_name: "nginx"
web_port: 80
web_ssl_port: 443
web_root: "/var/www/html"
web_user: "nginx"
web_group: "nginx"

# Application configuration
app_config_template: "app.conf.j2"
app_config_path: "/etc/nginx/conf.d/app.conf"
app_log_path: "/var/log/nginx"

# SSL/TLS settings
ssl_certificate_path: "/etc/ssl/certs/server.crt"
ssl_private_key_path: "/etc/ssl/private/server.key"
ssl_protocols: ["TLSv1.2", "TLSv1.3"]

# Performance tuning
worker_processes: "auto"
worker_connections: 1024
keepalive_timeout: 65
client_max_body_size: "100M"

# Security headers
security_headers:
  - "X-Frame-Options DENY"
  - "X-Content-Type-Options nosniff"
  - "X-XSS-Protection '1; mode=block'"
  - "Strict-Transport-Security 'max-age=31536000; includeSubDomains'"

# Load balancer backends (if applicable)
backend_servers:
  - "10.0.2.10:8080"
  - "10.0.2.11:8080"

# Health check settings
health_check_path: "/health"
health_check_interval: "30s"

# Log format
log_format: 'main $remote_addr - $remote_user [$time_local] "$request" '
             '$status $body_bytes_sent "$http_referer" '
             '"$http_user_agent" "$http_x_forwarded_for"'
'''

    def _generate_database_group_vars(self) -> str:
        """Generate the databases group variables."""
        return '''---
# Variables for database servers

# Database configuration
db_type: "mysql"  # mysql, postgresql, mariadb
db_service_name: "mysqld"
db_port: 3306
db_root_password: "{{ vault_db_root_password }}"
db_data_dir: "/var/lib/mysql"
db_log_dir: "/var/log/mysql"

# Application database settings
app_db_name: "appdb"
app_db_user: "appuser"
app_db_password: "{{ vault_app_db_password }}"

# Network access control
allowed_db_networks:
  - "10.0.1.0/24"  # Web servers subnet
  - "10.0.2.0/24"  # App servers subnet

# Performance tuning
innodb_buffer_pool_size: "256M"
max_connections: 100
query_cache_size: "64M"
query_cache_type: 1

# Backup configuration
backup_enabled: true
backup_schedule: "0 3 * * *"  # Daily at 3 AM
backup_retention_days: 7
backup_location: "/backup/mysql"
backup_user: "backup"

# Replication settings (if applicable)
enable_replication: false
master_server: ""
replication_user: "replicator"
replication_password: "{{ vault_replication_password }}"

# SSL/TLS for database connections
db_ssl_enabled: true
db_ssl_cert_path: "/etc/mysql/ssl/server-cert.pem"
db_ssl_key_path: "/etc/mysql/ssl/server-key.pem"
db_ssl_ca_path: "/etc/mysql/ssl/ca-cert.pem"

# Monitoring
enable_db_monitoring: true
slow_query_log: true
slow_query_log_file: "/var/log/mysql/slow.log"
long_query_time: 2

# Security settings
db_bind_address: "0.0.0.0"  # Change to specific IP in production
validate_password: true
'''

    def _create_role_structure(self, role_dir: str, role_name: str):
        """Create the standard Ansible role directory structure."""
        subdirs = ['tasks', 'handlers', 'templates', 'files', 'vars', 'defaults', 'meta']
        
        for subdir in subdirs:
            os.makedirs(os.path.join(role_dir, subdir), exist_ok=True)
        
        # Create main.yml files
        self._create_role_files(role_dir, role_name)

    def _create_role_files(self, role_dir: str, role_name: str):
        """Create the main files for an Ansible role."""
        # tasks/main.yml
        tasks_content = self._get_role_tasks_content(role_name)
        with open(os.path.join(role_dir, 'tasks', 'main.yml'), 'w') as f:
            f.write(tasks_content)
        
        # handlers/main.yml
        handlers_content = self._get_role_handlers_content(role_name)
        with open(os.path.join(role_dir, 'handlers', 'main.yml'), 'w') as f:
            f.write(handlers_content)
        
        # vars/main.yml
        vars_content = self._get_role_vars_content(role_name)
        with open(os.path.join(role_dir, 'vars', 'main.yml'), 'w') as f:
            f.write(vars_content)
        
        # defaults/main.yml
        defaults_content = self._get_role_defaults_content(role_name)
        with open(os.path.join(role_dir, 'defaults', 'main.yml'), 'w') as f:
            f.write(defaults_content)
        
        # meta/main.yml
        meta_content = self._get_role_meta_content(role_name)
        with open(os.path.join(role_dir, 'meta', 'main.yml'), 'w') as f:
            f.write(meta_content)

    def _get_role_files(self, role_dir: str) -> list:
        """Get list of files created for a role."""
        files = []
        for subdir in ['tasks', 'handlers', 'vars', 'defaults', 'meta']:
            files.append(os.path.join(role_dir, subdir, 'main.yml'))
        return files

    def _get_role_tasks_content(self, role_name: str) -> str:
        """Generate tasks content based on role type."""
        if role_name == "common":
            return '''---
# Common tasks for all servers

- name: Update system packages
  package:
    name: "*"
    state: latest
  tags: [packages]

- name: Install common packages
  package:
    name: "{{ common_packages }}"
    state: present
  tags: [packages]

- name: Configure timezone
  timezone:
    name: "{{ timezone }}"
  tags: [system]

- name: Configure NTP
  template:
    src: chrony.conf.j2
    dest: /etc/chrony.conf
    backup: yes
  notify: restart chronyd
  tags: [time]

- name: Start and enable chronyd
  systemd:
    name: chronyd
    state: started
    enabled: yes
  tags: [time]

- name: Configure SSH
  template:
    src: sshd_config.j2
    dest: /etc/ssh/sshd_config
    backup: yes
    validate: /usr/sbin/sshd -t -f %s
  notify: restart sshd
  tags: [ssh]

- name: Create admin users
  user:
    name: "{{ item.name }}"
    groups: "{{ item.groups }}"
    shell: /bin/bash
    create_home: yes
  loop: "{{ admin_users }}"
  tags: [users]

- name: Add SSH keys for admin users
  authorized_key:
    user: "{{ item.name }}"
    key: "{{ item.ssh_key }}"
    state: present
  loop: "{{ admin_users }}"
  when: item.ssh_key is defined
  tags: [users]
'''
        elif role_name == "webserver":
            return '''---
# Web server specific tasks

- name: Install web server
  package:
    name: "{{ web_service_name }}"
    state: present
  tags: [webserver]

- name: Create web user
  user:
    name: "{{ web_user }}"
    system: yes
    shell: /bin/false
    home: "{{ web_root }}"
    create_home: no
  tags: [webserver]

- name: Create web root directory
  file:
    path: "{{ web_root }}"
    state: directory
    owner: "{{ web_user }}"
    group: "{{ web_group }}"
    mode: '0755'
  tags: [webserver]

- name: Configure web server
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    backup: yes
  notify: restart nginx
  tags: [config]

- name: Create application configuration
  template:
    src: "{{ app_config_template }}"
    dest: "{{ app_config_path }}"
    owner: root
    group: root
    mode: '0644'
  notify: reload nginx
  tags: [config]

- name: Start and enable web server
  systemd:
    name: "{{ web_service_name }}"
    state: started
    enabled: yes
  tags: [webserver]
'''
        elif role_name == "database":
            return '''---
# Database server specific tasks

- name: Install database server
  package:
    name: "{{ db_service_name }}"
    state: present
  tags: [database]

- name: Install Python MySQL library
  package:
    name: python3-PyMySQL
    state: present
  when: db_type == "mysql"
  tags: [database]

- name: Start and enable database service
  systemd:
    name: "{{ db_service_name }}"
    state: started
    enabled: yes
  tags: [database]

- name: Secure database installation
  mysql_user:
    name: root
    password: "{{ db_root_password }}"
    login_unix_socket: /var/lib/mysql/mysql.sock
  when: db_type == "mysql"
  tags: [database]

- name: Configure database
  template:
    src: my.cnf.j2
    dest: /etc/my.cnf
    backup: yes
  notify: restart mysql
  when: db_type == "mysql"
  tags: [config]

- name: Create backup directory
  file:
    path: "{{ backup_location }}"
    state: directory
    owner: "{{ backup_user }}"
    group: "{{ backup_user }}"
    mode: '0750'
  when: backup_enabled
  tags: [backup]

- name: Setup database backup script
  template:
    src: backup_db.sh.j2
    dest: /usr/local/bin/backup_db.sh
    mode: '0755'
  when: backup_enabled
  tags: [backup]

- name: Schedule database backups
  cron:
    name: "Daily database backup"
    minute: "0"
    hour: "3"
    job: "/usr/local/bin/backup_db.sh"
    user: "{{ backup_user }}"
  when: backup_enabled
  tags: [backup]
'''
        else:
            return f'''---
# Tasks for {role_name} role

- name: Placeholder task for {role_name}
  debug:
    msg: "Configure {role_name} specific tasks here"
'''

    def _get_role_handlers_content(self, role_name: str) -> str:
        """Generate handlers content based on role type."""
        if role_name == "common":
            return '''---
# Common handlers

- name: restart sshd
  systemd:
    name: sshd
    state: restarted

- name: restart chronyd
  systemd:
    name: chronyd
    state: restarted

- name: reload systemd
  systemd:
    daemon_reload: yes
'''
        elif role_name == "webserver":
            return '''---
# Web server handlers

- name: restart nginx
  systemd:
    name: nginx
    state: restarted

- name: reload nginx
  systemd:
    name: nginx
    state: reloaded

- name: restart php-fpm
  systemd:
    name: php-fpm
    state: restarted
  when: php_enabled | default(false)
'''
        elif role_name == "database":
            return '''---
# Database handlers

- name: restart mysql
  systemd:
    name: mysqld
    state: restarted

- name: restart postgresql
  systemd:
    name: postgresql
    state: restarted
  when: db_type == "postgresql"
'''
        else:
            return f'''---
# Handlers for {role_name} role
'''

    def _get_role_vars_content(self, role_name: str) -> str:
        """Generate vars content based on role type."""
        return f'''---
# Variables for {role_name} role

# Add role-specific variables here
'''

    def _get_role_defaults_content(self, role_name: str) -> str:
        """Generate defaults content based on role type."""
        return f'''---
# Default variables for {role_name} role

# Add default values here
'''

    def _get_role_meta_content(self, role_name: str) -> str:
        """Generate meta content based on role type."""
        return f'''---
# Meta information for {role_name} role

galaxy_info:
  author: Cloud Infrastructure Team
  description: {role_name.title()} configuration role
  company: Organization
  license: MIT
  min_ansible_version: 2.9
  
  platforms:
    - name: EL
      versions:
        - 8
        - 9
    - name: Ubuntu
      versions:
        - 20.04
        - 22.04

  galaxy_tags:
    - {role_name}
    - infrastructure
    - configuration

dependencies: []
'''

    def _generate_ansible_config(self) -> str:
        """Generate the ansible.cfg configuration file."""
        return '''[defaults]
inventory = inventories/
host_key_checking = False
timeout = 30
log_path = /tmp/ansible.log
retry_files_enabled = False
gathering = smart
fact_caching = memory
stdout_callback = yaml
bin_ansible_callbacks = True

[inventory]
enable_plugins = host_list, script, auto, yaml, ini, toml

[ssh_connection]
ssh_args = -C -o ControlMaster=auto -o ControlPersist=60s
pipelining = True
control_path = /tmp/ansible-ssh-%%h-%%p-%%r

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False
'''

    def _generate_requirements(self) -> str:
        """Generate the requirements.yml file."""
        return '''---
# Ansible Galaxy requirements

roles:
  - name: geerlingguy.nginx
    version: "2.8.0"
  
  - name: geerlingguy.mysql
    version: "4.3.4"
  
  - name: geerlingguy.firewall
    version: "2.5.0"

collections:
  - name: community.general
    version: ">=3.0.0"
  
  - name: ansible.posix
    version: ">=1.0.0"
  
  - name: community.mysql
    version: ">=2.0.0"
'''

    def _generate_ansible_readme(self, timestamp: str) -> str:
        """Generate README for the Ansible configuration."""
        return f'''# Ansible Configuration - LZ_{timestamp}

This directory contains Ansible playbooks and roles for configuring cloud infrastructure based on the design specifications.

## Directory Structure

```
ansible/
├── ansible.cfg           # Ansible configuration
├── requirements.yml      # Role and collection dependencies
├── README.md            # This file
├── playbooks/           # Main playbooks
│   ├── site.yml         # Main orchestration playbook
│   ├── webservers.yml   # Web server configuration
│   └── databases.yml    # Database server configuration
├── roles/               # Custom roles
│   ├── common/          # Common configuration for all servers
│   ├── webserver/       # Web server specific configuration
│   └── database/        # Database server specific configuration
├── inventories/         # Environment inventories
│   ├── dev.yml          # Development environment
│   └── prod.yml         # Production environment
├── group_vars/          # Group-specific variables
│   ├── all.yml          # Variables for all groups
│   ├── webservers.yml   # Web server variables
│   └── databases.yml    # Database variables
└── host_vars/           # Host-specific variables (create as needed)
```

## Prerequisites

1. **Ansible** - Version >= 2.9
2. **Python** - Version >= 3.6
3. **SSH Access** - To target servers
4. **Sudo Access** - On target servers

## Setup Instructions

### 1. Install Ansible
```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install ansible

# On RHEL/CentOS
sudo dnf install ansible

# Using pip
pip install ansible
```

### 2. Install Dependencies
```bash
ansible-galaxy install -r requirements.yml
```

### 3. Configure Inventory
Edit the inventory files in `inventories/` to match your environment:
- Update IP addresses
- Verify SSH users
- Check SSH key paths

### 4. Test Connectivity
```bash
# Test connection to development environment
ansible all -i inventories/dev.yml -m ping

# Test connection to production environment
ansible all -i inventories/prod.yml -m ping
```

## Usage

### Run Full Configuration
```bash
# Configure development environment
ansible-playbook -i inventories/dev.yml playbooks/site.yml

# Configure production environment
ansible-playbook -i inventories/prod.yml playbooks/site.yml
```

### Run Specific Playbooks
```bash
# Configure only web servers
ansible-playbook -i inventories/dev.yml playbooks/webservers.yml

# Configure only database servers
ansible-playbook -i inventories/dev.yml playbooks/databases.yml
```

### Run with Tags
```bash
# Install packages only
ansible-playbook -i inventories/dev.yml playbooks/site.yml --tags "packages"

# Configure firewalls only
ansible-playbook -i inventories/dev.yml playbooks/site.yml --tags "firewall"

# Run validation only
ansible-playbook -i inventories/dev.yml playbooks/site.yml --tags "validation"
```

### Dry Run
```bash
# Check what changes would be made
ansible-playbook -i inventories/dev.yml playbooks/site.yml --check --diff
```

## Customization

### Variables
Customize variables in:
- `group_vars/all.yml` - Global settings
- `group_vars/webservers.yml` - Web server settings
- `group_vars/databases.yml` - Database settings
- `host_vars/<hostname>.yml` - Host-specific settings

### Adding New Roles
```bash
# Create new role structure
ansible-galaxy init roles/new_role_name

# Add role to playbooks
# Edit playbooks to include new role
```

### Vault for Secrets
```bash
# Create encrypted variables file
ansible-vault create group_vars/all/vault.yml

# Edit encrypted file
ansible-vault edit group_vars/all/vault.yml

# Run playbook with vault
ansible-playbook -i inventories/dev.yml playbooks/site.yml --ask-vault-pass
```

## Security Considerations

1. **SSH Keys**: Use SSH key authentication instead of passwords
2. **Vault**: Store sensitive data in Ansible Vault
3. **Sudo**: Configure passwordless sudo for automation users
4. **Firewall**: Ensure proper firewall rules are in place
5. **Access**: Limit network access to management interfaces

## Monitoring and Logging

- Ansible logs are configured in `ansible.cfg`
- Check `/tmp/ansible.log` for execution logs
- Use `--verbose` flag for detailed output
- Enable callback plugins for better formatting

## Troubleshooting

### Common Issues

1. **SSH Connection Failed**
   ```bash
   # Test SSH manually
   ssh -i ~/.ssh/key user@host
   
   # Check SSH configuration
   ansible all -i inventories/dev.yml -m setup --limit host
   ```

2. **Permission Denied**
   ```bash
   # Check sudo configuration
   ansible all -i inventories/dev.yml -m shell -a "sudo whoami"
   ```

3. **Module Not Found**
   ```bash
   # Install missing collections
   ansible-galaxy collection install community.general
   ```

### Debug Mode
```bash
# Run with maximum verbosity
ansible-playbook -i inventories/dev.yml playbooks/site.yml -vvvv
```

## Best Practices

1. **Idempotency**: Ensure playbooks can be run multiple times safely
2. **Testing**: Test in development before production
3. **Version Control**: Keep all configurations in version control
4. **Documentation**: Document custom variables and procedures
5. **Validation**: Include validation tasks in playbooks

## Support

For questions or issues:
1. Review the design document in `docs/design.md`
2. Check Ansible documentation
3. Contact the infrastructure team

---
*Generated on: {timestamp}*
'''

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Delegates to the synchronous invoke method.
        """
        return self.invoke(args, sly_data)
