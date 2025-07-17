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
        """Parse design document to extract infrastructure requirements dynamically."""
        requirements = {
            "cloud_provider": self._detect_cloud_provider(design_content),
            "region": self._extract_region(design_content),
            "resources": self._extract_resources(design_content),
            "networking": self._extract_networking(design_content),
            "security": self._extract_security(design_content),
            "monitoring": self._extract_monitoring(design_content),
            "backup": self._extract_backup(design_content),
            "scaling": self._extract_scaling(design_content),
            "compliance": self._extract_compliance(design_content)
        }
        
        return requirements

    def _detect_cloud_provider(self, content: str) -> str:
        """Detect cloud provider from design document."""
        content_lower = content.lower()
        
        if "aws" in content_lower or "amazon" in content_lower:
            return "aws"
        elif "azure" in content_lower or "microsoft" in content_lower:
            return "azure"
        elif "gcp" in content_lower or "google cloud" in content_lower:
            return "gcp"
        else:
            return "unknown"

    def _extract_region(self, content: str) -> str:
        """Extract region information from design document."""
        import re
        
        # AWS regions
        aws_regions = re.findall(r'us-[a-z]+-\d+|eu-[a-z]+-\d+|ap-[a-z]+-\d+', content.lower())
        if aws_regions:
            return aws_regions[0]
        
        # Azure regions
        azure_regions = re.findall(r'(east us|west us|north europe|west europe|southeast asia)', content.lower())
        if azure_regions:
            return azure_regions[0].replace(' ', '')
        
        # GCP regions
        gcp_regions = re.findall(r'us-central\d+|us-east\d+|us-west\d+|europe-west\d+', content.lower())
        if gcp_regions:
            return gcp_regions[0]
        
        return "us-east-1"  # Default

    def _extract_resources(self, content: str) -> Dict[str, Any]:
        """Extract specific cloud resources from design document."""
        content_lower = content.lower()
        resources = {
            "compute": [],
            "storage": [],
            "database": [],
            "networking": [],
            "security": [],
            "analytics": [],
            "serverless": []
        }
        
        # Extract compute resources
        if "ec2" in content_lower or "virtual machine" in content_lower:
            resources["compute"].append("ec2" if "aws" in content_lower else "vm")
        if "lambda" in content_lower:
            resources["serverless"].append("lambda")
        if "cloud functions" in content_lower:
            resources["serverless"].append("cloud_functions")
        if "azure functions" in content_lower:
            resources["serverless"].append("azure_functions")
        
        # Extract storage resources
        if "s3" in content_lower:
            resources["storage"].append("s3")
        if "blob storage" in content_lower:
            resources["storage"].append("blob_storage")
        if "cloud storage" in content_lower:
            resources["storage"].append("cloud_storage")
        
        # Extract database resources
        if "rds" in content_lower:
            resources["database"].append("rds")
        if "sql database" in content_lower:
            resources["database"].append("sql_database")
        if "cloud sql" in content_lower:
            resources["database"].append("cloud_sql")
        if "dynamodb" in content_lower:
            resources["database"].append("dynamodb")
        if "cosmosdb" in content_lower:
            resources["database"].append("cosmosdb")
        
        return resources

    def _extract_networking(self, content: str) -> Dict[str, Any]:
        """Extract networking requirements from design document."""
        content_lower = content.lower()
        networking = {
            "vpc_required": "vpc" in content_lower or "virtual network" in content_lower,
            "subnets": [],
            "load_balancers": [],
            "dns": [],
            "vpn": "vpn" in content_lower,
            "nat_gateway": "nat" in content_lower
        }
        
        # Extract load balancer types
        if "application load balancer" in content_lower or "alb" in content_lower:
            networking["load_balancers"].append("alb")
        if "network load balancer" in content_lower or "nlb" in content_lower:
            networking["load_balancers"].append("nlb")
        if "application gateway" in content_lower:
            networking["load_balancers"].append("application_gateway")
        
        return networking

    def _extract_security(self, content: str) -> Dict[str, Any]:
        """Extract security requirements from design document."""
        content_lower = content.lower()
        security = {
            "encryption": "encryption" in content_lower,
            "key_management": [],
            "access_control": [],
            "monitoring": [],
            "compliance": []
        }
        
        # Key management
        if "kms" in content_lower:
            security["key_management"].append("kms")
        if "key vault" in content_lower:
            security["key_management"].append("key_vault")
        
        # Access control
        if "iam" in content_lower:
            security["access_control"].append("iam")
        if "rbac" in content_lower:
            security["access_control"].append("rbac")
        if "sso" in content_lower:
            security["access_control"].append("sso")
        
        return security

    def _extract_monitoring(self, content: str) -> Dict[str, Any]:
        """Extract monitoring requirements from design document."""
        content_lower = content.lower()
        monitoring = {
            "enabled": "monitoring" in content_lower or "observability" in content_lower,
            "logging": [],
            "metrics": [],
            "alerting": []
        }
        
        if "cloudwatch" in content_lower:
            monitoring["logging"].append("cloudwatch")
        if "azure monitor" in content_lower:
            monitoring["logging"].append("azure_monitor")
        if "stackdriver" in content_lower:
            monitoring["logging"].append("stackdriver")
        
        return monitoring

    def _extract_backup(self, content: str) -> Dict[str, Any]:
        """Extract backup requirements from design document."""
        content_lower = content.lower()
        return {
            "enabled": "backup" in content_lower or "disaster recovery" in content_lower,
            "retention": self._extract_retention_period(content_lower),
            "cross_region": "cross-region" in content_lower or "cross region" in content_lower
        }

    def _extract_scaling(self, content: str) -> Dict[str, Any]:
        """Extract scaling requirements from design document."""
        content_lower = content.lower()
        return {
            "auto_scaling": "auto scaling" in content_lower or "autoscaling" in content_lower,
            "load_balancing": "load balancing" in content_lower,
            "high_availability": "high availability" in content_lower or "multi-az" in content_lower
        }

    def _extract_compliance(self, content: str) -> list:
        """Extract compliance requirements from design document."""
        content_lower = content.lower()
        compliance = []
        
        if "gdpr" in content_lower:
            compliance.append("gdpr")
        if "hipaa" in content_lower:
            compliance.append("hipaa")
        if "sox" in content_lower:
            compliance.append("sox")
        if "pci" in content_lower:
            compliance.append("pci")
        
        return compliance

    def _extract_retention_period(self, content: str) -> str:
        """Extract backup retention period from design document."""
        import re
        
        # Look for patterns like "30 days", "7 days", "1 year"
        retention_pattern = r'(\d+)\s*(day|week|month|year)s?'
        matches = re.findall(retention_pattern, content)
        
        if matches:
            return f"{matches[0][0]} {matches[0][1]}s"
        
        return "30 days"  # Default

    def _generate_main_playbook(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Generate main Ansible playbook based on requirements."""
        cloud_provider = requirements.get("cloud_provider", "azure")
        
        if cloud_provider == "azure":
            return self._generate_azure_playbook(project_name, requirements)
        elif cloud_provider == "aws":
            return self._generate_aws_playbook(project_name, requirements)
        elif cloud_provider == "gcp":
            return self._generate_gcp_playbook(project_name, requirements)
        else:
            return self._generate_azure_playbook(project_name, requirements)

    def _generate_azure_playbook(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Generate Azure-specific Ansible playbook."""
        tasks = []
        
        # Add compute configuration
        compute_resources = requirements.get("resources", {}).get("compute", [])
        if "vm" in compute_resources:
            tasks.append("      - name: Configure Azure Virtual Machine")
            tasks.append("        include_tasks: tasks/azure_vm.yml")
        
        # Add storage configuration
        storage_resources = requirements.get("resources", {}).get("storage", [])
        if "blob_storage" in storage_resources:
            tasks.append("      - name: Configure Azure Blob Storage")
            tasks.append("        include_tasks: tasks/azure_storage.yml")
        
        # Add database configuration
        database_resources = requirements.get("resources", {}).get("database", [])
        if "sql_database" in database_resources:
            tasks.append("      - name: Configure Azure SQL Database")
            tasks.append("        include_tasks: tasks/azure_sql.yml")
        
        # Add security configuration
        security_config = requirements.get("security", {})
        if security_config.get("encryption", False):
            tasks.append("      - name: Configure Azure Key Vault")
            tasks.append("        include_tasks: tasks/azure_keyvault.yml")
        
        # Add monitoring configuration
        monitoring_config = requirements.get("monitoring", {})
        if monitoring_config.get("enabled", False):
            tasks.append("      - name: Configure Azure Monitor")
            tasks.append("        include_tasks: tasks/azure_monitor.yml")
        
        # Add backup configuration
        backup_config = requirements.get("backup", {})
        if backup_config.get("enabled", False):
            tasks.append("      - name: Configure Azure Backup")
            tasks.append("        include_tasks: tasks/azure_backup.yml")
        
        tasks_content = "\n".join(tasks) if tasks else "      - name: Basic Azure setup\n        debug:\n          msg: 'No specific Azure services configured'"
        
        return f"""---
- name: Deploy {project_name} Infrastructure on Azure
  hosts: all
  become: yes
  
  vars:
    project_name: {project_name}
    cloud_provider: azure
    region: {requirements.get("region", "eastus")}
    
  vars_files:
    - vars/main.yml
    - vars/azure.yml
    
  tasks:
{tasks_content}
"""

    def _generate_aws_playbook(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Generate AWS-specific Ansible playbook."""
        tasks = []
        
        # Add compute configuration
        compute_resources = requirements.get("resources", {}).get("compute", [])
        if "ec2" in compute_resources:
            tasks.append("      - name: Configure EC2 Instance")
            tasks.append("        include_tasks: tasks/aws_ec2.yml")
        
        # Add storage configuration
        storage_resources = requirements.get("resources", {}).get("storage", [])
        if "s3" in storage_resources:
            tasks.append("      - name: Configure S3 Bucket")
            tasks.append("        include_tasks: tasks/aws_s3.yml")
        
        # Add database configuration
        database_resources = requirements.get("resources", {}).get("database", [])
        if "rds" in database_resources:
            tasks.append("      - name: Configure RDS Database")
            tasks.append("        include_tasks: tasks/aws_rds.yml")
        
        # Add security configuration
        security_config = requirements.get("security", {})
        if security_config.get("encryption", False):
            tasks.append("      - name: Configure AWS KMS")
            tasks.append("        include_tasks: tasks/aws_kms.yml")
        
        # Add monitoring configuration
        monitoring_config = requirements.get("monitoring", {})
        if monitoring_config.get("enabled", False):
            tasks.append("      - name: Configure CloudWatch")
            tasks.append("        include_tasks: tasks/aws_cloudwatch.yml")
        
        # Add backup configuration
        backup_config = requirements.get("backup", {})
        if backup_config.get("enabled", False):
            tasks.append("      - name: Configure AWS Backup")
            tasks.append("        include_tasks: tasks/aws_backup.yml")
        
        tasks_content = "\n".join(tasks) if tasks else "      - name: Basic AWS setup\n        debug:\n          msg: 'No specific AWS services configured'"
        
        return f"""---
- name: Deploy {project_name} Infrastructure on AWS
  hosts: all
  become: yes
  
  vars:
    project_name: {project_name}
    cloud_provider: aws
    region: {requirements.get("region", "us-east-1")}
    
  vars_files:
    - vars/main.yml
    - vars/aws.yml
    
  tasks:
{tasks_content}
"""

    def _generate_gcp_playbook(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Generate GCP-specific Ansible playbook."""
        tasks = []
        
        # Add compute configuration
        compute_resources = requirements.get("resources", {}).get("compute", [])
        if "compute_instance" in compute_resources:
            tasks.append("      - name: Configure GCP Compute Instance")
            tasks.append("        include_tasks: tasks/gcp_compute.yml")
        
        # Add storage configuration
        storage_resources = requirements.get("resources", {}).get("storage", [])
        if "cloud_storage" in storage_resources:
            tasks.append("      - name: Configure GCP Cloud Storage")
            tasks.append("        include_tasks: tasks/gcp_storage.yml")
        
        # Add database configuration
        database_resources = requirements.get("resources", {}).get("database", [])
        if "cloud_sql" in database_resources:
            tasks.append("      - name: Configure GCP Cloud SQL")
            tasks.append("        include_tasks: tasks/gcp_sql.yml")
        
        # Add security configuration
        security_config = requirements.get("security", {})
        if security_config.get("encryption", False):
            tasks.append("      - name: Configure GCP KMS")
            tasks.append("        include_tasks: tasks/gcp_kms.yml")
        
        # Add monitoring configuration
        monitoring_config = requirements.get("monitoring", {})
        if monitoring_config.get("enabled", False):
            tasks.append("      - name: Configure GCP Monitoring")
            tasks.append("        include_tasks: tasks/gcp_monitoring.yml")
        
        # Add backup configuration
        backup_config = requirements.get("backup", {})
        if backup_config.get("enabled", False):
            tasks.append("      - name: Configure GCP Backup")
            tasks.append("        include_tasks: tasks/gcp_backup.yml")
        
        tasks_content = "\n".join(tasks) if tasks else "      - name: Basic GCP setup\n        debug:\n          msg: 'No specific GCP services configured'"
        
        return f"""---
- name: Deploy {project_name} Infrastructure on GCP
  hosts: all
  become: yes
  
  vars:
    project_name: {project_name}
    cloud_provider: gcp
    region: {requirements.get("region", "us-central1")}
    
  vars_files:
    - vars/main.yml
    - vars/gcp.yml
"""

    def _generate_inventory(self, requirements: Dict[str, Any]) -> str:
        """Generate Ansible inventory file based on requirements."""
        cloud_provider = requirements.get("cloud_provider", "azure")
        
        if cloud_provider == "azure":
            return self._generate_azure_inventory(requirements)
        elif cloud_provider == "aws":
            return self._generate_aws_inventory(requirements)
        elif cloud_provider == "gcp":
            return self._generate_gcp_inventory(requirements)
        else:
            return self._generate_azure_inventory(requirements)

    def _generate_azure_inventory(self, requirements: Dict[str, Any]) -> str:
        """Generate Azure-specific inventory."""
        return """[all:vars]
ansible_user=azureuser
ansible_ssh_private_key_file=~/.ssh/id_rsa

[azure_vms]
vm1 ansible_host=10.0.1.10
vm2 ansible_host=10.0.1.11

[azure_databases]
sqldb1 ansible_host=sql-server.database.windows.net

[azure_storage]
storage1 ansible_host=storageaccount.blob.core.windows.net

[production:children]
azure_vms
azure_databases
azure_storage
"""

    def _generate_aws_inventory(self, requirements: Dict[str, Any]) -> str:
        """Generate AWS-specific inventory."""
        return """[all:vars]
ansible_user=ec2-user
ansible_ssh_private_key_file=~/.ssh/aws-key.pem

[ec2_instances]
web1 ansible_host=10.0.1.10
web2 ansible_host=10.0.1.11

[rds_databases]
db1 ansible_host=mydb.cluster-xyz.us-west-2.rds.amazonaws.com

[s3_storage]
s3bucket ansible_host=s3.amazonaws.com

[production:children]
ec2_instances
rds_databases
s3_storage
"""

    def _generate_gcp_inventory(self, requirements: Dict[str, Any]) -> str:
        """Generate GCP-specific inventory."""
        return """[all:vars]
ansible_user=gcp-user
ansible_ssh_private_key_file=~/.ssh/gcp-key

[gcp_instances]
instance1 ansible_host=10.0.1.10
instance2 ansible_host=10.0.1.11

[gcp_databases]
cloudsql1 ansible_host=sql-instance.region.gcp.project.com

[gcp_storage]
bucket1 ansible_host=storage.googleapis.com

[production:children]
gcp_instances
gcp_databases
gcp_storage
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
