#!/usr/bin/env python3
"""
CrewAI Agent Deployment Orchestrator MVP
Analyzes CrewAI agent codebases and generates Docker configurations
"""

import ast
import re
import os
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
import docker
import subprocess


class CrewAIAnalyzer:
    """Analyzes CrewAI agent definitions to extract dependencies and requirements"""
    
    def __init__(self, agent_path: str):
        self.agent_path = Path(agent_path)
        self.dependencies: Set[str] = set()
        self.system_requirements: Set[str] = set()
        self.agent_info: Dict[str, Any] = {}
        
    def analyze_python_file(self, file_path: Path) -> None:
        """Parse Python file for imports and CrewAI-specific patterns"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Parse AST
            tree = ast.parse(content)
            
            # Find imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.dependencies.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.dependencies.add(node.module.split('.')[0])
                
                # Look for CrewAI patterns
                if isinstance(node, ast.ClassDef):
                    # Check if this is a CrewAI agent
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            if 'Agent' in base.id or 'Crew' in base.id:
                                self.agent_info[node.name] = {
                                    'type': base.id,
                                    'file': file_path.name
                                }
            
            # Find pip install patterns
            pip_patterns = re.findall(r'pip\s+install\s+([^\s&|]+)', content)
            for dep in pip_patterns:
                self.dependencies.add(dep.strip("'\"`"))
                
            # Find system package patterns
            apt_patterns = re.findall(r'apt-get\s+install\s+([^\s&|]+)', content)
            for pkg in apt_patterns:
                self.system_requirements.add(pkg)
                
        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")
    
    def analyze_requirements_file(self, file_path: Path) -> None:
        """Parse requirements.txt or similar files"""
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name (remove version specifiers)
                        pkg = line.split('>')[0].split('<')[0].split('=')[0].split('~')[0]
                        pkg = pkg.strip()
                        if pkg:
                            self.dependencies.add(pkg)
        except Exception as e:
            print(f"Warning: Could not parse requirements file {file_path}: {e}")
    
    def analyze_directory(self) -> Dict[str, Any]:
        """Analyze the entire agent directory"""
        python_files = list(self.agent_path.rglob("*.py"))
        req_files = list(self.agent_path.rglob("requirements*.txt"))
        req_files += list(self.agent_path.rglob("setup.py"))
        req_files += list(self.agent_path.rglob("pyproject.toml"))
        
        # Analyze Python files
        for py_file in python_files:
            self.analyze_python_file(py_file)
        
        # Analyze requirements files
        for req_file in req_files:
            self.analyze_requirements_file(req_file)
        
        # Look for additional config files
        config_files = list(self.agent_path.rglob("*.yml")) + list(self.agent_path.rglob("*.yaml"))
        for config_file in config_files:
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                    # Look for common dependencies in configs
                    if isinstance(config, dict):
                        if 'dependencies' in config:
                            deps = config['dependencies']
                            if isinstance(deps, list):
                                self.dependencies.update(deps)
            except:
                pass
        
        return {
            'dependencies': sorted(list(self.dependencies)),
            'system_requirements': sorted(list(self.system_requirements)),
            'agents_found': self.agent_info,
            'python_files': len(python_files),
            'config_files': len(config_files)
        }


class DockerConfigGenerator:
    """Generates Docker configurations for CrewAI agents"""
    
    def __init__(self, analysis_results: Dict[str, Any], output_dir: str):
        self.analysis = analysis_results
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_dockerfile(self) -> str:
        """Generate optimized Dockerfile"""
        deps = self.analysis['dependencies']
        
        # Base image selection
        base_image = "python:3.11-slim"
        
        dockerfile = f"""# CrewAI Agent Deployment
FROM {base_image}

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    {" \\\n    ".join(self.analysis['system_requirements'])} && \\
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.connect(('localhost', 8000))" || exit 1

# Expose default port
EXPOSE 8000

# Default command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        
        # Write Dockerfile
        dockerfile_path = self.output_dir / "Dockerfile"
        dockerfile_path.write_text(dockerfile)
        
        # Create requirements.txt if not exists
        req_path = self.output_dir / "requirements.txt"
        if not req_path.exists():
            req_path.write_text("\n".join(deps))
        
        return str(dockerfile_path)
    
    def generate_docker_compose(self, agent_name: str = "crewai-agent") -> str:
        """Generate docker-compose.yml with monitoring setup"""
        
        compose = f"""version: '3.8'

services:
  {agent_name}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    
  # Monitoring service (optional)
  monitor:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped

volumes:
  prometheus-data:
    driver: local
"""
        
        compose_path = self.output_dir / "docker-compose.yml"
        compose_path.write_text(compose)
        
        # Create basic prometheus config
        prometheus_config = """global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'crewai-agent'
    static_configs:
      - targets: ['crewai-agent:8000']
"""
        
        prometheus_path = self.output_dir / "prometheus.yml"
        prometheus_path.write_text(prometheus_config)
        
        return str(compose_path)
    
    def generate_health_check(self) -> str:
        """Generate health check endpoint"""
        health_check = """from fastapi import FastAPI, Response
import psutil
import os

app = FastAPI()

@app.get("/health")
async def health_check():
    '''Health check endpoint for monitoring'''
    try:
        # Check memory usage
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        
        return {
            "status": "healthy",
            "memory_percent": memory.percent,
            "cpu_percent": cpu,
            "agent_count": len(agents) if 'agents' in globals() else 0
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
        
        health_path = self.output_dir / "health_check.py"
        health_path.write_text(health_check)
        
        return str(health_path)


def main():
    parser = argparse.ArgumentParser(description="CrewAI Agent Deployment Orchestrator")
    parser.add_argument("agent_path", help="Path to CrewAI agent directory")
    parser.add_argument("--output", "-o", default="./deployment", 
                       help="Output directory for generated configs")
    parser.add_argument("--agent-name", default="crewai-agent",
                       help="Name for the Docker service")
    
    args = parser.parse_args()
    
    print(f"Analyzing CrewAI agent at: {args.agent_path}")
    
    # Analyze the agent
    analyzer = CrewAIAnalyzer(args.agent_path)
    results = analyzer.analyze_directory()
    
    print(f"Analysis complete:")
    print(f"  Found {results['python_files']} Python files")
    print(f"  Found {len(results['agents_found'])} agent definitions")
    print(f"  Dependencies: {len(results['dependencies'])} packages")
    print(f"  System requirements: {len(results['system_requirements'])} packages")
    
    # Generate deployment configurations
    generator = DockerConfigGenerator(results, args.output)
    
    print("\nGenerating deployment configurations...")
    dockerfile = generator.generate_dockerfile()
    compose = generator.generate_docker_compose(args.agent_name)
    health_check = generator.generate_health_check()
    
    print(f"Generated files:")
    print(f"  ✓ Dockerfile: {dockerfile}")
    print(f"  ✓ docker-compose.yml: {compose}")
    print(f"  ✓ health_check.py: {health_check}")
    print(f"  ✓ requirements.txt: {os.path.join(args.output, 'requirements.txt')}")
    print(f"  ✓ prometheus.yml: {os.path.join(args.output, 'prometheus.yml')}")
    
    print(f"\nDeployment configurations saved to: {args.output}")
    print("\nTo deploy:")
    print(f"  cd {args.output}")
    print(f"  docker-compose up -d")


if __name__ == "__main__":
    main()
