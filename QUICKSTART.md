# Quick Start Guide

## Installation

```bash
cd agent_deploy_orchestrator
pip install -r requirements.txt
```

## Basic Usage

### CLI Wrapper (Recommended)

Use the simplified CLI wrapper for easier deployment:

```bash
# Using the CLI wrapper
python orchestrator-cli.py examples/simple_agent \
 --output deployments/simple \
 --agent-name simple-agent
```

### 1. Analyze and Deploy Simple Agent

```bash
# Generate deployment configuration (alternative: direct script)
python src/enhanced_orchestrator.py examples/simple_agent \
 --output deployments/simple \
 --agent-name simple-agent

# Deploy
cd deployments/simple
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Access health endpoint
curl http://localhost:8000/health
```

### 2. Deploy Web Research Agent

```bash
# Generate deployment configuration
python orchestrator-cli.py examples/web_research_agent \
 --output deployments/web-research \
 --agent-name web-research

# Deploy
cd deployments/web-research
docker-compose up -d
```

### 3. Access Monitoring

```
Grafana: http://localhost:3000 (admin/admin)
Prometheus: http://localhost:9090
Agent API: http://localhost:8000
```

## Test Suite

```bash
# Run standard tests
python test_orchestrator.py

# Run enhanced tests
python test_enhanced_orchestrator.py

# Phase 2 validation (all tests must pass)
python test_enhanced_orchestrator.py && python test_orchestrator.py
```

## Generated Files

For each deployment, you get:

```
deployments/simple/
├── Dockerfile # Container definition
├── docker-compose.yml # Service orchestration
├── requirements.txt # Python dependencies
├── health_check.py # Health endpoints
├── prometheus.yml # Monitoring config
└── grafana/
 ├── provisioning/
 │ └── datasources/datasource.yml
 └── dashboard.json # Grafana dashboard
```

## Custom Agent Deployment

For your own CrewAI agent:

```bash
# Point to your agent directory (using CLI wrapper)
python orchestrator-cli.py /path/to/your/agent \
 --output deployments/my-agent \
 --agent-name my-agent

# Or use the direct script
python src/enhanced_orchestrator.py /path/to/your/agent \
 --output deployments/my-agent \
 --agent-name my-agent

# Copy your agent code to deployment folder
cp -r /path/to/your/agent/* deployments/my-agent/

# Deploy
cd deployments/my-agent
docker-compose up -d
```

## Health Endpoints

```
/health - Full health check
/ready - Readiness probe
/live - Liveness probe
/metrics - Prometheus metrics
```

## Troubleshooting

### Build fails
```bash
docker builder prune -a
docker-compose build --no-cache
```

### Port conflicts
Edit `docker-compose.yml` and change port mappings:
```yaml
ports:
 - "8001:8000" # Use different host port
```

### View detailed logs
```bash
docker-compose logs -f simple-agent
docker-compose logs -f prometheus
docker-compose logs -f grafana
```

## Next Steps

1. Customize `docker-compose.yml` for your needs
2. Set environment variables (API keys, etc.)
3. Configure resource limits
4. Set up alerts in Grafana
5. Deploy to production

For detailed documentation, see:
- `README.md` - Main documentation
- `ENHANCED_README.md` - Enhanced features
- `MVP_SUMMARY.md` - Complete summary
- `PHASE2_TEST_RESULTS.md` - Phase 2 test results
