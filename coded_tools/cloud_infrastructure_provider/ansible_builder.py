import os
from typing import Dict, Any, Union
from pathlib import Path
from neuro_san.interfaces.coded_tool import CodedTool


class AnsibleBuilder(CodedTool):
    def __init__(self):
        super().__init__()
        self.tool_name = "ansible_builder"
        self.description = "Generate Ansible playbooks and configurations for infrastructure deployment"

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        try:
            project_name = args.get("project_name", "sample_project")
            output_dir = args.get("output_dir", f"output/{project_name}")
            
            # Read design document to extract requirements
            design_path = os.path.join(output_dir, "docs", "design.md")
            if os.path.exists(design_path):
                with open(design_path, 'r') as f:
                    design_content = f.read()
                requirements = self._parse_design_requirements(design_content)
            else:
                # Default minimal requirements
                requirements = {
                    "services": ["nginx"],
                    "databases": [],
                    "load_balancers": [],
                    "monitoring": False,
                    "ssl": False,
                    "backup": False,
                    "security": [],
                    "networking": {},
                    "scaling": {}
                }
            
            # Create Ansible directory structure
            ansible_dir = os.path.join(output_dir, "ansible")
            os.makedirs(ansible_dir, exist_ok=True)
            os.makedirs(os.path.join(ansible_dir, "tasks"), exist_ok=True)
            os.makedirs(os.path.join(ansible_dir, "templates"), exist_ok=True)
            os.makedirs(os.path.join(ansible_dir, "vars"), exist_ok=True)
            
            # Generate main playbook
            playbook_content = self._generate_main_playbook(project_name, requirements)
            with open(os.path.join(ansible_dir, "playbook.yml"), 'w') as f:
                f.write(playbook_content)
            
            # Generate inventory
            inventory_content = self._generate_inventory(requirements)
            with open(os.path.join(ansible_dir, "inventory.ini"), 'w') as f:
                f.write(inventory_content)
            
            # Generate task files
            self._generate_task_files(ansible_dir, requirements)
            
            # Generate variables file
            vars_content = self._generate_variables(project_name, requirements)
            with open(os.path.join(ansible_dir, "vars", "main.yml"), 'w') as f:
                f.write(vars_content)
            
            return {
                "success": True,
                "message": f"Ansible configuration generated for {project_name}",
                "files_created": [
                    f"{ansible_dir}/playbook.yml",
                    f"{ansible_dir}/inventory.ini",
                    f"{ansible_dir}/vars/main.yml"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate Ansible configuration: {str(e)}"
            }

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        return self.invoke(args, sly_data)

    def _parse_design_requirements(self, design_content: str) -> Dict[str, Any]:
        """Parse design document to extract infrastructure requirements."""
        requirements = {
            "services": [],
            "databases": [],
            "load_balancers": [],
            "monitoring": False,
            "ssl": False,
            "backup": False,
            "security": [],
            "networking": {},
            "scaling": {}
        }
        
        content_lower = design_content.lower()
        
        # Parse services from design
        if "nginx" in content_lower or "web server" in content_lower:
            requirements["services"].append("nginx")
        if "apache" in content_lower:
            requirements["services"].append("apache")
        if "docker" in content_lower or "container" in content_lower:
            requirements["services"].append("docker")
        if "redis" in content_lower:
            requirements["services"].append("redis")
        if "elasticsearch" in content_lower:
            requirements["services"].append("elasticsearch")
            
        # Parse databases
        if "postgresql" in content_lower or "postgres" in content_lower:
            requirements["databases"].append("postgresql")
        if "mysql" in content_lower:
            requirements["databases"].append("mysql")
        if "mongodb" in content_lower:
            requirements["databases"].append("mongodb")
            
        # Parse infrastructure components
        if "load balancer" in content_lower or "load balancing" in content_lower:
            requirements["load_balancers"].append("nginx")
            
        # Parse monitoring requirements
        requirements["monitoring"] = "monitoring" in content_lower or "metrics" in content_lower
        
        # Parse security requirements
        if "ssl" in content_lower or "tls" in content_lower or "https" in content_lower:
            requirements["ssl"] = True
        if "firewall" in content_lower:
            requirements["security"].append("firewall")
        if "fail2ban" in content_lower or "intrusion" in content_lower:
            requirements["security"].append("fail2ban")
            
        # Parse backup requirements
        requirements["backup"] = "backup" in content_lower or "disaster recovery" in content_lower
        
        return requirements

    def _generate_main_playbook(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Generate main Ansible playbook based on requirements."""
        tasks = []
        
        # Add service tasks based on requirements
        for service in requirements.get("services", []):
            if service == "nginx":
                tasks.append("      - name: Install and configure Nginx")
                tasks.append("        include_tasks: tasks/nginx.yml")
            elif service == "apache":
                tasks.append("      - name: Install and configure Apache")
                tasks.append("        include_tasks: tasks/apache.yml")
            elif service == "docker":
                tasks.append("      - name: Install and configure Docker")
                tasks.append("        include_tasks: tasks/docker.yml")
            elif service == "redis":
                tasks.append("      - name: Install and configure Redis")
                tasks.append("        include_tasks: tasks/redis.yml")
                
        # Add database tasks
        for db in requirements.get("databases", []):
            if db == "postgresql":
                tasks.append("      - name: Install and configure PostgreSQL")
                tasks.append("        include_tasks: tasks/postgresql.yml")
            elif db == "mysql":
                tasks.append("      - name: Install and configure MySQL")
                tasks.append("        include_tasks: tasks/mysql.yml")
            elif db == "mongodb":
                tasks.append("      - name: Install and configure MongoDB")
                tasks.append("        include_tasks: tasks/mongodb.yml")
                
        # Add security tasks
        for security in requirements.get("security", []):
            if security == "firewall":
                tasks.append("      - name: Configure firewall")
                tasks.append("        include_tasks: tasks/firewall.yml")
            elif security == "fail2ban":
                tasks.append("      - name: Install and configure Fail2ban")
                tasks.append("        include_tasks: tasks/fail2ban.yml")
                
        # Add monitoring if required
        if requirements.get("monitoring", False):
            tasks.append("      - name: Install monitoring tools")
            tasks.append("        include_tasks: tasks/monitoring.yml")
            
        # Add backup if required
        if requirements.get("backup", False):
            tasks.append("      - name: Configure backup system")
            tasks.append("        include_tasks: tasks/backup.yml")
        
        tasks_content = "\n".join(tasks) if tasks else "      - name: Basic system setup\n        debug:\n          msg: 'No specific services configured'"
        
        return f"""---
- name: Deploy {project_name} Infrastructure
  hosts: all
  become: yes
  
  vars:
    project_name: {project_name}
    ssl_enabled: {str(requirements.get("ssl", False)).lower()}
    
  tasks:
{tasks_content}
    
    - name: Ensure all services are started and enabled
      systemd:
        name: "{{{{ item }}}}"
        state: started
        enabled: yes
      loop: {requirements.get("services", [])}
      ignore_errors: yes
"""

    def _generate_inventory(self, requirements: Dict[str, Any]) -> str:
        """Generate Ansible inventory file based on requirements."""
        return """[all:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file=~/.ssh/id_rsa

[webservers]
web1 ansible_host=10.0.1.10
web2 ansible_host=10.0.1.11

[databases]
db1 ansible_host=10.0.2.10

[monitoring]
monitor1 ansible_host=10.0.3.10

[production:children]
webservers
databases
monitoring
"""

    def _generate_task_files(self, ansible_dir: str, requirements: Dict[str, Any]) -> None:
        """Generate individual task files based on requirements."""
        tasks_dir = os.path.join(ansible_dir, "tasks")
        
        # Generate nginx task if needed
        if "nginx" in requirements.get("services", []):
            nginx_content = self._generate_nginx_task(requirements)
            with open(os.path.join(tasks_dir, "nginx.yml"), 'w') as f:
                f.write(nginx_content)
        
        # Generate database tasks
        for db in requirements.get("databases", []):
            if db == "postgresql":
                postgres_content = self._generate_postgresql_task(requirements)
                with open(os.path.join(tasks_dir, "postgresql.yml"), 'w') as f:
                    f.write(postgres_content)
                    
        # Generate security tasks
        if "firewall" in requirements.get("security", []):
            firewall_content = self._generate_firewall_task(requirements)
            with open(os.path.join(tasks_dir, "firewall.yml"), 'w') as f:
                f.write(firewall_content)

    def _generate_nginx_task(self, requirements: Dict[str, Any]) -> str:
        """Generate Nginx task file based on requirements."""
        ssl_config = ""
        if requirements.get("ssl", False):
            ssl_config = """
- name: Configure SSL certificate
  copy:
    content: |
      # SSL configuration here
    dest: /etc/nginx/ssl/{{ project_name }}.conf
        
- name: Enable SSL in Nginx
  lineinfile:
    path: /etc/nginx/sites-available/{{ project_name }}
    line: '    listen 443 ssl;'
    insertafter: '    listen 80;'
"""
        
        return f"""---
- name: Install Nginx
  package:
    name: nginx
    state: present

- name: Start and enable Nginx
  systemd:
    name: nginx
    state: started
    enabled: yes

- name: Create Nginx configuration
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/sites-available/{{{{ project_name }}}}
    backup: yes

- name: Enable site
  file:
    src: /etc/nginx/sites-available/{{{{ project_name }}}}
    dest: /etc/nginx/sites-enabled/{{{{ project_name }}}}
    state: link

- name: Remove default site
  file:
    path: /etc/nginx/sites-enabled/default
    state: absent{ssl_config}

- name: Test Nginx configuration
  command: nginx -t
  notify: reload nginx

- name: Ensure Nginx is reloaded
  systemd:
    name: nginx
    state: reloaded
"""

    def _generate_postgresql_task(self, requirements: Dict[str, Any]) -> str:
        """Generate PostgreSQL task file based on requirements."""
        return """---
- name: Install PostgreSQL
  package:
    name:
      - postgresql
      - postgresql-contrib
      - python3-psycopg2
    state: present

- name: Start and enable PostgreSQL
  systemd:
    name: postgresql
    state: started
    enabled: yes

- name: Create database
  postgresql_db:
    name: "{{ project_name }}_db"
    state: present
  become_user: postgres

- name: Create database user
  postgresql_user:
    name: "{{ project_name }}_user"
    password: "{{ db_password }}"
    db: "{{ project_name }}_db"
    priv: ALL
    state: present
  become_user: postgres
"""

    def _generate_firewall_task(self, requirements: Dict[str, Any]) -> str:
        """Generate firewall task file based on requirements."""
        return """---
- name: Install UFW
  package:
    name: ufw
    state: present

- name: Allow SSH
  ufw:
    rule: allow
    port: '22'
    proto: tcp

- name: Allow HTTP
  ufw:
    rule: allow
    port: '80'
    proto: tcp

- name: Allow HTTPS
  ufw:
    rule: allow
    port: '443'
    proto: tcp
  when: ssl_enabled | bool

- name: Enable UFW
  ufw:
    state: enabled
    policy: deny
    direction: incoming
"""

    def _generate_variables(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Generate variables file based on project requirements."""
        return f"""---
# Project variables for {project_name}
project_name: "{project_name}"
environment: "production"

# Database configuration
db_password: "{{ vault_db_password }}"

# SSL configuration
ssl_enabled: {str(requirements.get("ssl", False)).lower()}

# Services
services: {requirements.get("services", [])}

# Security
firewall_enabled: {"true" if "firewall" in requirements.get("security", []) else "false"}

# Monitoring
monitoring_enabled: {str(requirements.get("monitoring", False)).lower()}

# Backup
backup_enabled: {str(requirements.get("backup", False)).lower()}
"""
