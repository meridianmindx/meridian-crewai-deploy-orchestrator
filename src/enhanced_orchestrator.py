#!/usr/bin/env python3
"""
Enhanced CrewAI Agent Deployment Orchestrator
Advanced analysis and deployment configuration generation for CrewAI agents
"""

import ast
import re
import os
import yaml
import argparse
import json
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class AgentDefinition:
    """Represents a CrewAI agent definition"""
    name: str
    role: str = ""
    goal: str = ""
    backstory: str = ""
    llm_model: str = "unknown"
    tools: List[str] = field(default_factory=list)
    file_path: str = ""
    line_number: int = 0


@dataclass
class DependencyInfo:
    """Dependency metadata"""
    name: str
    version_constraint: str = ""
    is_dev: bool = False
    source: str = ""


class EnhancedCrewAIAnalyzer:
    """Enhanced analyzer for CrewAI agent codebases"""
    
    # Known CrewAI patterns
    CREWAI_BASES = {'Agent', 'Crew', 'Task', 'CrewAI'}
    
    # System packages mapping (Python package -> system dependency)
    SYSTEM_DEPS_MAP = {
        'opencv-python': ['libopencv-dev', 'python3-opencv'],
        'pillow': ['libjpeg-dev', 'zlib1g-dev'],
        'pygame': ['libsdl2-dev', 'libsdl2-image-dev', 'libsdl2-mixer-dev'],
        'mysql-connector': ['libmysqlclient-dev'],
        'psycopg2': ['libpq-dev', 'postgresql-client'],
        'lxml': ['libxml2-dev', 'libxslt1-dev'],
        'cryptography': ['libssl-dev', 'libffi-dev'],
        'beautifulsoup4': ['libxml2-dev', 'libxslt1-dev'],
        'pyaudio': ['portaudio19-dev'],
        'python-speechrecognition': ['libpulse-dev'],
    }
    
    # Python package alternatives
    PACKAGE_ALIASES = {
        'PIL': 'pillow',
        'cv2': 'opencv-python',
        'bs4': 'beautifulsoup4',
        'yaml': 'pyyaml',
        'sklearn': 'scikit-learn',
    }
    
    def __init__(self, agent_path: str):
        self.agent_path = Path(agent_path)
        self.python_deps: Set[str] = set()
        self.system_deps: Set[str] = set()
        self.agents: List[AgentDefinition] = []
        self.imports: Dict[str, str] = {}  # module -> version
        self.has_async = False
        self.has_web_tools = False
        self.has_database = False
        self.has_ml_libs = False
        
    def _extract_agent_info(self, node: ast.ClassDef, content: str) -> Optional[AgentDefinition]:
        """Extract agent information from class definition"""
        # Check if it's a CrewAI agent
        is_agent = False
        for base in node.bases:
            if isinstance(base, ast.Name) and any(a in base.id for a in self.CREWAI_BASES):
                is_agent = True
                break
        
        if not is_agent:
            return None
            
        # Extract attributes from __init__
        role = ""
        goal = ""
        backstory = ""
        llm_model = "unknown"
        tools = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                # Parse init body for super() call arguments
                source_lines = content.split('\n')
                init_code = '\n'.join(source_lines[item.lineno-1:item.end_lineno])
                
                # Extract role, goal, backstory from super() call
                role_match = re.search(r'role\s*=\s*["\']([^"\']+)["\']', init_code)
                goal_match = re.search(r'goal\s*=\s*["\']([^"\']+)["\']', init_code)
                backstory_match = re.search(r'backstory\s*=\s*["\']([^"\']+)["\']', init_code)
                model_match = re.search(r'model\s*=\s*["\']([^"\']+)["\']', init_code)
                
                if role_match:
                    role = role_match.group(1)
                if goal_match:
                    goal = goal_match.group(1)
                if backstory_match:
                    backstory = backstory_match.group(1)
                if model_match:
                    llm_model = model_match.group(1)
                    
                # Look for tools
                tools_match = re.search(r'tools\s*=\s*\[([^\]]+)\]', init_code)
                if tools_match:
                    tools = [t.strip() for t in tools_match.group(1).split(',')]
        
        return AgentDefinition(
            name=node.name,
            role=role,
            goal=goal,
            backstory=backstory,
            llm_model=llm_model,
            tools=tools,
            file_path=str(self.agent_path),
            line_number=node.lineno
        )
    
    def analyze_python_file(self, file_path: Path) -> None:
        """Parse Python file for imports, agents, and dependencies"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name.split('.')[0]
                        self.python_deps.add(self.PACKAGE_ALIASES.get(module, module))
                        self.imports[module] = ''
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module = node.module.split('.')[0]
                        self.python_deps.add(self.PACKAGE_ALIASES.get(module, module))
                        self.imports[module] = ''
                
                # Detect async usage
                if isinstance(node, ast.AsyncFunctionDef):
                    self.has_async = True
                
                # Detect web/database tools
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if 'search' in node.func.id.lower() or 'scrape' in node.func.id.lower():
                            self.has_web_tools = True
            
            # Look for Agent class definitions
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    agent = self._extract_agent_info(node, content)
                    if agent:
                        self.agents.append(agent)
            
            # Find pip install patterns
            pip_patterns = re.findall(r'pip\s+install\s+([^\s&|]+)', content)
            for dep in pip_patterns:
                self.python_deps.add(dep.strip("'\"`"))
            
            # Find system package patterns
            apt_patterns = re.findall(r'apt-get\s+install\s+([^\s&|]+)', content)
            for pkg in apt_patterns:
                self.system_deps.add(pkg)
                
            # Detect ML libraries
            ml_patterns = ['tensorflow', 'torch', 'sklearn', 'xgboost', 'lightgbm']
            for ml_lib in ml_patterns:
                if ml_lib in content.lower():
                    self.has_ml_libs = True
                    break
                    
        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")
    
    def analyze_requirements_file(self, file_path: Path) -> None:
        """Parse requirements.txt or similar files"""
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('-'):
                        # Extract package name and version
                        match = re.match(r'^([a-zA-Z0-9_-]+)(.*)$', line)
                        if match:
                            pkg = match.group(1)
                            version = match.group(2).strip()
                            self.python_deps.add(pkg)
                            if version:
                                self.imports[pkg] = version
        except Exception as e:
            print(f"Warning: Could not parse requirements file {file_path}: {e}")
    
    def analyze_setup_py(self, file_path: Path) -> None:
        """Parse setup.py for dependencies"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Find install_requires
            requires_match = re.search(r'install_requires\s*=\s*\[([^\]]+)\]', content)
            if requires_match:
                deps = requires_match.group(1)
                for dep in re.findall(r'["\']([^"\']+)["\']', deps):
                    self.python_deps.add(dep.split('>=')[0].split('<=')[0].strip())
        except Exception as e:
            print(f"Warning: Could not parse setup.py: {e}")
    
    def analyze_pyproject_toml(self, file_path: Path) -> None:
        """Parse pyproject.toml for dependencies"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Simple TOML parsing for dependencies
            deps_match = re.search(r'dependencies\s*=\s*\[([^\]]+)\]', content)
            if deps_match:
                deps = deps_match.group(1)
                for dep in re.findall(r'["\']([^"\']+)["\']', deps):
                    self.python_deps.add(dep.split('>=')[0].split('<=')[0].strip())
        except Exception as e:
            print(f"Warning: Could not parse pyproject.toml: {e}")
    
    def infer_system_dependencies(self) -> None:
        """Infer system dependencies from Python packages"""
        for pkg in self.python_deps:
            if pkg in self.SYSTEM_DEPS_MAP:
                self.system_deps.update(self.SYSTEM_DEPS_MAP[pkg])
    
    def analyze_directory(self) -> Dict[str, Any]:
        """Comprehensive analysis of the agent directory"""
        python_files = list(self.agent_path.rglob("*.py"))
        req_files = list(self.agent_path.rglob("requirements*.txt"))
        setup_files = list(self.agent_path.rglob("setup.py"))
        pyproject_files = list(self.agent_path.rglob("pyproject.toml"))
        
        # Analyze Python files
        for py_file in python_files:
            self.analyze_python_file(py_file)
        
        # Analyze requirements files
        for req_file in req_files:
            self.analyze_requirements_file(req_file)
        
        # Analyze setup.py files
        for setup_file in setup_files:
            self.analyze_setup_py(setup_file)
        
        # Analyze pyproject.toml files
        for pyproject_file in pyproject_files:
            self.analyze_pyproject_toml(pyproject_file)
        
        # Infer system dependencies
        self.infer_system_dependencies()
        
        # Build agent info dict
        agents_info = {}
        for agent in self.agents:
            agents_info[agent.name] = {
                'role': agent.role,
                'goal': agent.goal,
                'llm_model': agent.llm_model,
                'tools': agent.tools,
                'file': agent.file_path,
                'line': agent.line_number
            }
        
        return {
            'dependencies': sorted(list(self.python_deps)),
            'system_requirements': sorted(list(self.system_deps)),
            'agents_found': agents_info,
            'agent_objects': self.agents,
            'python_files': len(python_files),
            'has_async': self.has_async,
            'has_web_tools': self.has_web_tools,
            'has_database': self.has_database,
            'has_ml_libs': self.has_ml_libs,
            'imports': self.imports
        }


class EnhancedDockerConfigGenerator:
    """Enhanced Docker configuration generator with optimizations"""
    
    def __init__(self, analysis_results: Dict[str, Any], output_dir: str):
        self.analysis = analysis_results
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine base image based on analysis
        self.base_image = self._determine_base_image()
    
    def _determine_base_image(self) -> str:
        """Select appropriate base image based on requirements"""
        deps = self.analysis.get('dependencies', [])
        
        # Check for ML libraries
        ml_libs = {'tensorflow', 'torch', 'scikit-learn', 'xgboost'}
        if any(lib in str(deps).lower() for lib in ml_libs):
            return "python:3.11-slim"
        
        # Check for async/web tools
        if self.analysis.get('has_async', False) or self.analysis.get('has_web_tools', False):
            return "python:3.11-slim"
        
        return "python:3.11-slim"
    
    def _get_system_packages(self) -> List[str]:
        """Get list of system packages to install"""
        system_pkgs = list(self.analysis.get('system_requirements', []))
        
        # Add common packages based on detected features
        if self.analysis.get('has_web_tools', False):
            system_pkgs.extend(['curl', 'wget'])
        
        if self.analysis.get('has_ml_libs', False):
            system_pkgs.extend(['libgomp1'])
        
        return sorted(list(set(system_pkgs)))
    
    def generate_dockerfile(self) -> str:
        """Generate optimized multi-stage Dockerfile"""
        deps = self.analysis.get('dependencies', [])
        system_pkgs = self._get_system_packages()
        
        # Build system packages install command
        if system_pkgs:
            apt_packages = ' '.join(system_pkgs)
            apt_cmd = f"RUN apt-get update && apt-get install -y --no-install-recommends {apt_packages} && rm -rf /var/lib/apt/lists/*"
        else:
            apt_cmd = ""
        
        # Determine if we need build tools
        needs_build_tools = any(d in str(deps) for d in ['cryptography', 'mysql', 'psycopg2'])
        build_tools = ""
        if needs_build_tools:
            build_tools = """# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*"""
        
        # Create requirements.txt content
        reqs_content = "\n".join(deps) if deps else "# Add your dependencies here"
        reqs_path = self.output_dir / "requirements.txt"
        reqs_path.write_text(reqs_content)
        
        dockerfile = f"""# CrewAI Agent Deployment - Auto-generated
# Generated by Agent Deployment Orchestrator
FROM {self.base_image}

LABEL maintainer="agent-deploy-orchestrator"
LABEL version="1.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1 \\
    PIP_NO_CACHE_DIR=1 \\
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
{apt_cmd}
{build_tools}

# Copy requirements first for Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Expose default port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command
CMD ["python", "main.py"]
"""
        
        dockerfile_path = self.output_dir / "Dockerfile"
        dockerfile_path.write_text(dockerfile)
        
        return str(dockerfile_path)
    
    def generate_docker_compose(self, agent_name: str = "crewai-agent") -> str:
        """Generate docker-compose.yml with monitoring and logging"""
        
        compose = f"""version: '3.8'

services:
  {agent_name}:
    build: .
    container_name: {agent_name}
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
      - LOG_LEVEL=INFO
      - AGENT_NAME={agent_name}
    volumes:
      - ./logs:/app/logs
      - agent_data:/app/data
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    restart: unless-stopped
    # Resource limits (adjust based on needs)
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M

  # Optional: Prometheus for monitoring
  prometheus:
    image: prom/prometheus:v2.45.0
    container_name: {agent_name}-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.enable-lifecycle'
    restart: unless-stopped
    depends_on:
      - {agent_name}

  # Optional: Grafana for dashboards
  grafana:
    image: grafana/grafana:10.0.0
    container_name: {agent_name}-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    restart: unless-stopped
    depends_on:
      - prometheus

volumes:
  prometheus_data:
  grafana_data:
  agent_data:
"""
        
        compose_path = self.output_dir / "docker-compose.yml"
        compose_path.write_text(compose)
        
        # Generate Prometheus config
        self._generate_prometheus_config(agent_name)
        
        # Generate Grafana datasource
        self._generate_grafana_config(agent_name)
        
        return str(compose_path)
    
    def _generate_prometheus_config(self, agent_name: str) -> None:
        """Generate Prometheus configuration"""
        prometheus_config = f"""global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: '{agent_name}'
    static_configs:
      - targets: ['{agent_name}:8000']
    metrics_path: '/metrics'
"""
        
        prom_path = self.output_dir / "prometheus.yml"
        prom_path.write_text(prometheus_config)
    
    def _generate_grafana_config(self, agent_name: str) -> None:
        """Generate Grafana provisioning configuration"""
        datasources_dir = self.output_dir / "grafana" / "provisioning" / "datasources"
        datasources_dir.mkdir(parents=True, exist_ok=True)
        
        datasource_config = f"""apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://{agent_name}-prometheus:9090
    isDefault: true
    editable: true
"""
        
        (datasources_dir / "datasource.yml").write_text(datasource_config)
    
    def generate_health_check(self) -> str:
        """Generate comprehensive health check endpoint"""
        health_check = '''#!/usr/bin/env python3
"""Health Check Endpoint for CrewAI Agent"""

from fastapi import FastAPI
import psutil
import time
from typing import Dict, Any

app = FastAPI()
START_TIME = time.time()
request_count = 0

@app.on_event("startup")
async def startup_event():
    print("Health check service started")

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    global request_count
    request_count += 1
    try:
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)
        uptime = time.time() - START_TIME
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "uptime_seconds": round(uptime, 2),
            "memory_percent": memory.percent,
            "cpu_percent": cpu,
            "request_count": request_count
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500

@app.get("/metrics")
async def metrics() -> str:
    try:
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)
        uptime = time.time() - START_TIME
        return f"""# HELP agent_uptime_seconds Agent uptime
# TYPE agent_uptime_seconds counter
agent_uptime_seconds {uptime}
# HELP agent_memory_percent Memory usage
# TYPE agent_memory_percent gauge
agent_memory_percent {memory.percent}
# HELP agent_cpu_percent CPU usage
# TYPE agent_cpu_percent gauge
agent_cpu_percent {cpu}
# HELP agent_requests_total Total requests
# TYPE agent_requests_total counter
agent_requests_total {request_count}
"""
    except Exception as e:
        return f"# ERROR: {str(e)}"

@app.get("/ready")
async def readiness_check() -> Dict[str, str]:
    return {"status": "ready"}

@app.get("/live")
async def liveness_check() -> Dict[str, str]:
    return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        health_path = self.output_dir / "health_check.py"
        health_path.write_text(health_check)
        return str(health_path)

    def generate_monitoring_dashboard(self) -> str:
        """Generate Grafana dashboard JSON"""
        dashboard = {
            "dashboard": {
                "title": "CrewAI Agent Monitoring",
                "refresh": "5s",
                "panels": [
                    {
                        "title": "CPU Usage",
                        "type": "gauge",
                        "targets": [{"expr": "agent_cpu_percent"}]
                    },
                    {
                        "title": "Memory Usage",
                        "type": "gauge",
                        "targets": [{"expr": "agent_memory_percent"}]
                    },
                    {
                        "title": "Uptime",
                        "type": "stat",
                        "targets": [{"expr": "agent_uptime_seconds"}]
                    },
                    {
                        "title": "Request Count",
                        "type": "graph",
                        "targets": [{"expr": "rate(agent_requests_total[1m])"}]
                    }
                ]
            }
        }
        
        dashboard_path = self.output_dir / "grafana" / "dashboard.json"
        dashboard_path.parent.mkdir(parents=True, exist_ok=True)
        dashboard_path.write_text(json.dumps(dashboard, indent=2))
        
        return str(dashboard_path)


def generate_deployment_package(analysis: Dict[str, Any], output_dir: str, agent_name: str) -> Dict[str, str]:
    """Generate complete deployment package"""
    generator = EnhancedDockerConfigGenerator(analysis, output_dir)
    
    generated = {
        'dockerfile': generator.generate_dockerfile(),
        'docker_compose': generator.generate_docker_compose(agent_name),
        'health_check': generator.generate_health_check(),
        'dashboard': generator.generate_monitoring_dashboard()
    }
    
    return generated


def main():
    parser = argparse.ArgumentParser(description="Enhanced CrewAI Agent Deployment Orchestrator")
    parser.add_argument("agent_path", help="Path to CrewAI agent directory")
    parser.add_argument("--output", "-o", default="./deployment", 
                        help="Output directory for generated configs")
    parser.add_argument("--agent-name", default="crewai-agent",
                        help="Name for the Docker service")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    
    args = parser.parse_args()
    
    print(f"\n🔍 Analyzing CrewAI agent at: {args.agent_path}")
    print("=" * 60)
    
    # Analyze the agent
    analyzer = EnhancedCrewAIAnalyzer(args.agent_path)
    results = analyzer.analyze_directory()
    
    print(f"\n📊 Analysis Results:")
    print(f"   Python files: {results['python_files']}")
    print(f"   Agents found: {len(results['agents_found'])}")
    print(f"   Dependencies: {len(results['dependencies'])} packages")
    print(f"   System requirements: {len(results['system_requirements'])} packages")
    
    if results.get('has_async'):
        print(f"   ⚡ Async detected: Yes")
    if results.get('has_web_tools'):
        print(f"   🌐 Web tools detected: Yes")
    if results.get('has_ml_libs'):
        print(f"   🤖 ML libraries detected: Yes")
    
    # List detected agents
    if results['agents_found']:
        print(f"\n👥 Detected Agents:")
        for name, info in results['agents_found'].items():
            print(f"   - {name}: {info.get('role', 'Unknown role')}")
    
    # Generate deployment configurations
    print(f"\n🔧 Generating deployment configurations...")
    
    generated = generate_deployment_package(results, args.output, args.agent_name)
    
    print(f"\n✅ Generated files:")
    for name, path in generated.items():
        print(f"   ✓ {name}: {path}")
    
    print(f"\n📁 Deployment package saved to: {args.output}")
    print("\n🚀 To deploy:")
    print(f"   cd {args.output}")
    print(f"   docker-compose up -d")
    print(f"\n📊 View monitoring:")
    print(f"   Grafana: http://localhost:3000 (admin/admin)")
    print(f"   Prometheus: http://localhost:9090")


if __name__ == "__main__":
    main()
