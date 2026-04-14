<!-- schema.org metadata -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareSourceCode",
  "name": "meridian-crewai-deploy-orchestrator",
  "description": "Production deployment for CrewAI agents: Automated containerization, scaling, and monitoring for multi-agent AI systems.",
  "url": "https://github.com/meridianmindx/meridian-crewai-deploy-orchestrator",
  "codeRepository": "https://github.com/meridianmindx/meridian-crewai-deploy-orchestrator",
  "programmingLanguage": "Python",
  "license": "https://opensource.org/licenses/MIT",
  "dateCreated": "2026-04-08",
  "dateModified": "2026-04-14",
  "keywords": [
    "CrewAI",
    "multi-agent",
    "deployment",
    "Docker",
    "orchestration",
    "monitoring",
    "AI agents",
    "containerization"
  ],
  "author": {
    "@type": "Organization",
    "name": "Meridian Mind",
    "url": "https://github.com/meridianmindx"
  }
}
</script>

# Meridian CrewAI Agent Deployment Orchestrator

[![PyPI version](https://img.shields.io/pypi/v/meridian-crewai-deploy-orchestrator.svg)](https://pypi.org/project/meridian-crewai-deploy-orchestrator/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Build Status](https://github.com/meridianmindx/meridian-crewai-deploy-orchestrator/actions/workflows/build.yml/badge.svg)](https://github.com/meridianmindx/meridian-crewai-deploy-orchestrator/actions/workflows/build.yml) [![PyPI downloads](https://img.shields.io/pypi/dm/meridian-crewai-deploy-orchestrator.svg)](https://pypi.org/project/meridian-crewai-deploy-orchestrator/) [![GitHub stars](https://img.shields.io/github/stars/meridianmindx/meridian-crewai-deploy-orchestrator.svg?style=social)](https://github.com/meridianmindx/meridian-crewai-deploy-orchestrator/stargazers) [![Meridian Tooling](https://img.shields.io/badge/Part_of-Meridian_Tooling_Suite-3498db)](https://github.com/meridianmindx)

**Deploy CrewAI agents anywhere with one command.** Automatically analyze agent codebases and generate optimized Docker configurations for cloud deployment. The easiest way to containerize and scale your CrewAI agents.

## ⭐ Why this matters
- Stop manually writing Dockerfiles and docker-compose.yml
- Deploy CrewAI agents to AWS, GCP, Azure in minutes
- Built-in health checks and monitoring
- Perfect for production deployments

## 🚀 Quick Start

```bash
# Install
pip install meridian-crewai-deploy-orchestrator

# Analyze an agent and generate deployment configs
meridian-crewai-deploy-orchestrator /path/to/agent --output ./deployment

# Or use directly with Python
python -m orchestrator /path/to/agent --output ./deployment
```

## 📦 Installation

### From PyPI (recommended)

```bash
pip install meridian-crewai-deploy-orchestrator
```

### From Source (for development)

```bash
git clone https://github.com/meridianmindx/meridian-crewai-deploy-orchestrator.git
cd crewai-deploy-orchestrator
pip install -r requirements.txt
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## ✨ Features

- **Agent Analysis**: Parse CrewAI agent definitions to extract dependencies
- **Dependency Detection**: Identify Python packages and system requirements
- **Docker Generation**: Create optimized Dockerfile and docker-compose.yml
- **Health Monitoring**: Built-in health checks and monitoring setup
- **Multi-Platform**: Ready for cloud deployment (AWS, GCP, Azure, etc.)

## 📖 Usage Examples

### Basic Usage

```bash
# Analyze an agent and generate deployment configs
crewai-deploy /path/to/agent --output ./deployment

# With custom agent name
crewai-deploy /path/to/agent --output ./deployment --agent-name my-agent
```

### Example with Included Examples

```bash
# Test with included examples
crewai-deploy examples/simple_agent --output simple_deployment

# Deploy
cd simple_deployment
docker-compose up -d
```

### Output Structure

The tool generates the following files:

```
deployment/
├── Dockerfile           # Optimized container definition
├── docker-compose.yml   # Multi-service orchestration
├── requirements.txt     # Python dependencies
├── health_check.py      # Health monitoring endpoint
├── prometheus.yml       # Monitoring configuration
└── logs/                # Log directory (mounted volume)
```

## 🔍 How It Works

### 1. Agent Analysis

The tool scans your CrewAI agent codebase for:
- Python imports and dependencies
- Agent class definitions (Agent, CrewAI patterns)
- Requirements files (requirements.txt, setup.py, pyproject.toml)
- System package requirements (apt-get install patterns)

### 2. Dependency Resolution

- Extracts all Python package dependencies
- Identifies system-level requirements
- Creates optimized installation order

### 3. Docker Configuration

- Generates optimized Dockerfile with caching
- Creates docker-compose.yml with health checks
- Includes monitoring setup (Prometheus)
- Sets up volume mounts for persistence

### 4. Health Monitoring

- Built-in FastAPI health endpoint
- Resource usage monitoring (CPU, memory)
- Agent status reporting
- Ready for integration with monitoring stacks

## 🧪 Testing

Run the test suite:

```bash
python test_orchestrator.py
```

The test suite includes:
- Simple agent analysis
- Web research agent analysis 
- CLI interface testing
- Docker config generation

## 📦 Example Agents

The repository includes two example agents:

### 1. Simple Agent (`examples/simple_agent/`)
- Basic data analysis agent
- Report generation workflow
- Minimal dependencies

### 2. Web Research Agent (`examples/web_research_agent/`)
- Multi-agent research system
- Web scraping capabilities
- Async processing
- Comprehensive reporting

## 🚀 Deployment Options

### Local Development

```bash
docker-compose up -d
```

### Production Considerations

- Set environment variables for API keys
- Configure resource limits in docker-compose.yml
- Add SSL/TLS termination
- Set up proper logging and monitoring
- Implement backup strategies

### Cloud Deployment

- **AWS**: Deploy to ECS/EKS with Load Balancer
- **GCP**: Deploy to Cloud Run or GKE
- **Azure**: Deploy to Container Apps or AKS
- **Kubernetes**: Use generated manifests with `kompose convert`

## ⚙️ Configuration

### Environment Variables

```bash
# Agent configuration
OPENAI_API_KEY=your_key_here
LOG_LEVEL=INFO
PYTHONPATH=/app

# Docker configuration
MEMORY_LIMIT=2g
CPU_LIMIT=1.0
```

### Customizing Deployment

Edit generated files:
- `Dockerfile`: Add custom build steps
- `docker-compose.yml`: Adjust resource limits, add services
- `prometheus.yml`: Configure monitoring targets
- `health_check.py`: Add custom health checks

## ⚠️ Limitations (MVP)

- Currently supports Python/CrewAI agents only
- Basic dependency resolution (no conflict handling)
- Assumes FastAPI for health endpoints
- Limited system package detection
- No automatic cloud deployment integration

## 🗺️ Roadmap

- [ ] Advanced dependency conflict resolution
- [ ] Cloud provider templates (AWS, GCP, Azure)
- [ ] Kubernetes manifests generation
- [ ] Database and cache integration
- [ ] Secret management
- [ ] CI/CD pipeline templates
- [ ] Multi-language agent support
- [ ] Performance optimization recommendations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🌐 Community

- **GitHub Issues**: Report bugs and feature requests
- **Discussions**: Share ideas and ask questions
- **CrewAI Discord**: Join the CrewAI community

---

## 🔗 See Also

**Part of the Meridian Tooling Suite** – Complementary tools for AI agent development:

### 🚀 [Meridian MCP Deploy Framework](https://github.com/meridianmindx/meridian-mcp-deploy)
Deploy MCP servers with one command. Save hours of manual Docker configuration for Model Context Protocol (MCP) servers.

**Perfect companion for CrewAI deployments:** Deploy your MCP servers alongside CrewAI agents using the same unified approach.

### 🔄 [Meridian Context Compression](https://github.com/meridianmindx/meridian-context-compression)
Reduce LLM token usage by 22x while preserving semantic meaning. Cut your OpenAI and Anthropic API costs dramatically with intelligent context compression.

**Works great with CrewAI:** Compress prompts before sending to expensive LLMs, especially useful when CrewAI agents retrieve large documents.

### 📦 Installation Bundle

```bash
# Install the complete Meridian tooling suite
pip install meridian-crewai-deploy-orchestrator meridian-context-compression
# Or individually
pip install meridian-mcp-deploy
```

### 🎯 Why Use All Three?

1. **meridian-crewai-deploy-orchestrator**: Deploy your CrewAI agents
2. **meridian-mcp-deploy**: Containerize and deploy your MCP servers
3. **meridian-context-compression**: Optimize token usage for both

**Together, they provide a complete AI agent deployment and optimization stack.**

---

## ❤️ Support this project

If this tool helps you deploy CrewAI agents faster, please consider **starring this repository** on GitHub. Stars help other developers discover useful tools!

[⭐ Star this repo](https://github.com/meridianmindx/meridian-crewai-deploy-orchestrator/stargazers) • [💬 Start a discussion](https://github.com/meridianmindx/meridian-crewai-deploy-orchestrator/discussions) • [🐛 Report issues](https://github.com/meridianmindx/meridian-crewai-deploy-orchestrator/issues)

**Built for the CrewAI ecosystem** • Deploy agents anywhere with confidence

## 💰 Affiliate Disclosure

We participate in affiliate programs for cloud providers. If you sign up using our links, we may earn a commission at no extra cost to you. This helps support the project.

- **AWS**: [Sign up for AWS Free Tier](https://aws.amazon.com/free/?tag=meridian-20)
- **DigitalOcean**: [Get $200 credit](https://m.do.co/c/meridian-20)
- **GCP**: [Start with $300 free](https://cloud.google.com/free/?utm_source=meridian)

These links provide you with the same great deals and help us continue building open-source tools.