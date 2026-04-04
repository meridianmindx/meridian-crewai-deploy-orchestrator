# Enhanced CrewAI Agent Deployment Orchestrator

## Overview

The Enhanced Orchestrator provides advanced analysis and deployment configuration generation for CrewAI agents with comprehensive monitoring capabilities.

## Key Features

### 1. Advanced Agent Analysis
- **Deep AST Parsing**: Extracts agent definitions, roles, goals, and tools
- **Dependency Inference**: Automatically maps Python packages to system dependencies
- **Feature Detection**: Identifies async code, web tools, ML libraries, and database usage
- **Multi-format Support**: Analyzes requirements.txt, setup.py, pyproject.toml

### 2. Smart Docker Generation
- **Optimized Base Images**: Selects appropriate base image based on requirements
- **Layer Caching**: Optimizes Docker build cache for faster deployments
- **Resource Limits**: Pre-configured CPU and memory limits
- **Health Checks**: Built-in liveness and readiness probes

### 3. Comprehensive Monitoring
- **Prometheus Integration**: Pre-configured metrics collection
- **Grafana Dashboards**: Ready-to-use monitoring dashboards
- **Custom Metrics**: Agent-specific metrics (uptime, requests, resources)
- **Alerting Ready**: Configurable alert thresholds

## Usage

### Basic Usage

```bash
# Run enhanced analyzer
python src/enhanced_orchestrator.py /path/to/agent --output ./deployment --agent-name my-agent

# With verbose output
python src/enhanced_orchestrator.py /path/to/agent -o ./deployment -v
```

### Example: Simple Agent

```bash
python src/enhanced_orchestrator.py examples/simple_agent \
  --output deployments/simple \
  --agent-name simple-agent
```

### Example: Web Research Agent

```bash
python src/enhanced_orchestrator.py examples/web_research_agent \
  --output deployments/web-research \
  --agent-name web-research-agent
```

## Output Structure

```
deployment/
├── Dockerfile                    # Optimized container definition
├── docker-compose.yml            # Multi-service orchestration
├── requirements.txt              # Python dependencies
├── health_check.py               # Health monitoring endpoint
├── prometheus.yml                # Prometheus configuration
├── grafana/
│   ├── provisioning/
│   │   └── datasources/
│   │       └── datasource.yml    # Prometheus datasource
│   └── dashboard.json            # Pre-built Grafana dashboard
└── logs/                         # Log directory (mounted volume)
```

## Generated Services

### 1. Agent Service
- **Port**: 8000
- **Health Check**: /health, /ready, /live
- **Metrics**: /metrics (Prometheus format)
- **Resource Limits**: 2 CPU, 2GB memory (configurable)

### 2. Prometheus Service
- **Port**: 9090
- **Scrape Interval**: 15s
- **Data Retention**: Configurable

### 3. Grafana Service
- **Port**: 3000
- **Default Login**: admin/admin
- **Dashboards**: Auto-provisioned

## Health Endpoints

| Endpoint | Description | Use Case |
|----------|-------------|----------|
| `/health` | Full health check | Load balancer health |
| `/ready` | Readiness probe | Kubernetes readiness |
| `/live` | Liveness probe | Kubernetes liveness |
| `/metrics` | Prometheus metrics | Monitoring |

## Metrics Exposed

```
# Agent metrics
agent_uptime_seconds       - Time since startup
agent_memory_percent       - Memory usage %
agent_cpu_percent          - CPU usage %
agent_requests_total       - Total request count
```

## System Dependency Mapping

The orchestrator automatically maps common Python packages to system dependencies:

| Python Package | System Dependencies |
|----------------|--------------------|
| opencv-python | libopencv-dev, python3-opencv |
| pillow | libjpeg-dev, zlib1g-dev |
| mysql-connector | libmysqlclient-dev |
| psycopg2 | libpq-dev, postgresql-client |
| cryptography | libssl-dev, libffi-dev |
| beautifulsoup4 | libxml2-dev, libxslt1-dev |

## Deployment Examples

### Local Development

```bash
cd deployments/simple
docker-compose up -d

# View logs
docker-compose logs -f

# Check health
curl http://localhost:8000/health
```

### Production Deployment

```bash
# Set environment variables
export OPENAI_API_KEY="your-key"
export LOG_LEVEL="INFO"

# Deploy with resource limits
docker-compose --profile production up -d
```

### Kubernetes Deployment

```bash
# Convert to Kubernetes manifests
kompose convert -f docker-compose.yml

# Deploy to Kubernetes
kubectl apply -f .
```

## Advanced Configuration

### Custom Resource Limits

Edit `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 4G
    reservations:
      cpus: '1.0'
      memory: 1G
```

### Custom Health Checks

Edit `health_check.py` to add custom checks:

```python
@app.get("/health/custom")
async def custom_health():
    # Add custom health checks
    db_ok = check_database()
    api_ok = check_external_api()
    
    if db_ok and api_ok:
        return {"status": "healthy"}
    return {"status": "unhealthy"}, 500
```

### Custom Metrics

Add custom Prometheus metrics:

```python
from prometheus_client import Counter, Histogram

agent_tasks = Counter('agent_tasks_total', 'Total tasks processed')
task_duration = Histogram('agent_task_duration', 'Task duration')
```

## Troubleshooting

### Build Issues

```bash
# Clear Docker cache
docker builder prune -a

# Rebuild without cache
docker-compose build --no-cache
```

### Dependency Conflicts

```bash
# Check generated requirements
cat requirements.txt

# Test in isolation
docker run -it python:3.11-slim pip install -r requirements.txt
```

### Monitoring Issues

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Grafana datasources
curl http://localhost:3000/api/datasources
```

## Comparison: Standard vs Enhanced

| Feature | Standard | Enhanced |
|---------|----------|----------|
| Agent Detection | Basic | Deep AST parsing |
| Dependency Mapping | Manual | Automatic inference |
| Base Image | Fixed | Smart selection |
| Health Checks | Basic | Comprehensive |
| Monitoring | Prometheus only | Prometheus + Grafana |
| Dashboards | None | Pre-built |
| Resource Limits | None | Pre-configured |
| Kubernetes Ready | No | Yes |

## API Reference

### EnhancedCrewAIAnalyzer

```python
from src.enhanced_orchestrator import EnhancedCrewAIAnalyzer

analyzer = EnhancedCrewAIAnalyzer("path/to/agent")
results = analyzer.analyze_directory()

print(results['agents_found'])      # Detected agents
print(results['dependencies'])      # Python dependencies
print(results['system_requirements'])  # System packages
print(results['has_async'])         # Async code detected
print(results['has_web_tools'])     # Web tools detected
```

### EnhancedDockerConfigGenerator

```python
from src.enhanced_orchestrator import EnhancedDockerConfigGenerator

generator = EnhancedDockerConfigGenerator(results, "output_dir")
generator.generate_dockerfile()
generator.generate_docker_compose("my-agent")
generator.generate_health_check()
generator.generate_monitoring_dashboard()
```

## Best Practices

1. **Pin Dependencies**: Use specific versions in requirements.txt
2. **Test Health Checks**: Verify /health endpoint before deploying
3. **Set Resource Limits**: Adjust based on agent workload
4. **Monitor Metrics**: Set up alerts for critical metrics
5. **Use Volumes**: Persist data and logs outside containers

## Limitations

- Python/CrewAI agents only
- Basic TOML parsing for pyproject.toml
- Assumes FastAPI for health endpoints
- No automatic cloud deployment

## Roadmap

- [ ] Kubernetes manifest generation
- [ ] Cloud provider templates (AWS ECS, GCP Cloud Run)
- [ ] Secret management integration
- [ ] Multi-region deployment
- [ ] Auto-scaling configuration
- [ ] Database migration support
- [ ] CI/CD pipeline templates
