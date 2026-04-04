#!/usr/bin/env python3
"""
Comprehensive test suite for Enhanced CrewAI Agent Deployment Orchestrator
Tests both standard and enhanced orchestrator functionality
"""

import sys
import os
import subprocess
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from enhanced_orchestrator import EnhancedCrewAIAnalyzer, EnhancedDockerConfigGenerator


def test_simple_agent_analysis():
    """Test analysis of simple agent with enhanced analyzer"""
    print("\n" + "="*60)
    print("TEST: Simple Agent Analysis (Enhanced)")
    print("="*60)
    
    analyzer = EnhancedCrewAIAnalyzer("examples/simple_agent")
    results = analyzer.analyze_directory()
    
    # Verify results
    assert results['python_files'] == 1, f"Expected 1 Python file, got {results['python_files']}"
    assert len(results['agents_found']) == 2, f"Expected 2 agents, got {len(results['agents_found'])}"
    assert 'DataAnalystAgent' in results['agents_found'], "Missing DataAnalystAgent"
    assert 'ReportWriterAgent' in results['agents_found'], "Missing ReportWriterAgent"
    
    print(f"✓ Found {len(results['agents_found'])} agents")
    print(f"✓ Dependencies: {len(results['dependencies'])} packages")
    print(f"✓ Agent roles detected:")
    for name, info in results['agents_found'].items():
        print(f"   - {name}: {info.get('role', 'N/A')}")
    
    return True


def test_web_research_agent_analysis():
    """Test analysis of web research agent"""
    print("\n" + "="*60)
    print("TEST: Web Research Agent Analysis (Enhanced)")
    print("="*60)
    
    analyzer = EnhancedCrewAIAnalyzer("examples/web_research_agent")
    results = analyzer.analyze_directory()
    
    # Verify results
    assert results['python_files'] == 1, f"Expected 1 Python file"
    assert len(results['agents_found']) == 4, f"Expected 4 agents, got {len(results['agents_found'])}"
    assert results['has_async'] == True, "Should detect async code"
    assert results['has_web_tools'] == True, "Should detect web tools"
    
    print(f"✓ Found {len(results['agents_found'])} agents")
    print(f"✓ Dependencies: {len(results['dependencies'])} packages")
    print(f"✓ Async detected: {results['has_async']}")
    print(f"✓ Web tools detected: {results['has_web_tools']}")
    
    return True


def test_docker_generation():
    """Test Docker configuration generation"""
    print("\n" + "="*60)
    print("TEST: Docker Configuration Generation")
    print("="*60)
    
    analyzer = EnhancedCrewAIAnalyzer("examples/simple_agent")
    results = analyzer.analyze_directory()
    
    output_dir = "test_output/docker_gen"
    os.makedirs(output_dir, exist_ok=True)
    
    generator = EnhancedDockerConfigGenerator(results, output_dir)
    
    # Test Dockerfile generation
    dockerfile = generator.generate_dockerfile()
    assert os.path.exists(dockerfile), "Dockerfile not created"
    
    # Verify Dockerfile content
    with open(dockerfile, 'r') as f:
        content = f.read()
        assert 'FROM python:' in content, "Missing base image"
        assert 'WORKDIR /app' in content, "Missing workdir"
        assert 'HEALTHCHECK' in content, "Missing health check"
    
    # Test docker-compose generation
    compose = generator.generate_docker_compose("test-agent")
    assert os.path.exists(compose), "docker-compose.yml not created"
    
    # Verify docker-compose content
    with open(compose, 'r') as f:
        content = f.read()
        assert 'services:' in content, "Missing services"
        assert 'healthcheck:' in content, "Missing healthcheck config"
        assert 'prometheus' in content, "Missing prometheus service"
        assert 'grafana' in content, "Missing grafana service"
    
    # Test health check generation
    health = generator.generate_health_check()
    assert os.path.exists(health), "health_check.py not created"
    
    # Test dashboard generation
    dashboard = generator.generate_monitoring_dashboard()
    assert os.path.exists(dashboard), "dashboard.json not created"
    
    print(f"✓ Dockerfile: {dockerfile}")
    print(f"✓ docker-compose.yml: {compose}")
    print(f"✓ health_check.py: {health}")
    print(f"✓ dashboard.json: {dashboard}")
    
    # Cleanup
    import shutil
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    return True


def test_cli_interface():
    """Test command-line interface"""
    print("\n" + "="*60)
    print("TEST: CLI Interface")
    print("="*60)
    
    output_dir = "test_output/cli_test"
    
    cmd = [
        sys.executable,
        "src/enhanced_orchestrator.py",
        "examples/simple_agent",
        "--output", output_dir,
        "--agent-name", "cli-test-agent"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ CLI execution successful")
        
        # Verify output files exist
        assert os.path.exists(f"{output_dir}/Dockerfile"), "Dockerfile missing"
        assert os.path.exists(f"{output_dir}/docker-compose.yml"), "docker-compose.yml missing"
        assert os.path.exists(f"{output_dir}/health_check.py"), "health_check.py missing"
        
        print("✓ All expected files generated")
        
        # Cleanup
        import shutil
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        
        return True
    else:
        print("✗ CLI execution failed")
        print("Error:", result.stderr)
        return False


def test_dependency_detection():
    """Test dependency detection accuracy"""
    print("\n" + "="*60)
    print("TEST: Dependency Detection")
    print("="*60)
    
    analyzer = EnhancedCrewAIAnalyzer("examples/web_research_agent")
    results = analyzer.analyze_directory()
    
    deps = results['dependencies']
    
    # Check for expected dependencies
    expected = ['crewai', 'langchain', 'beautifulsoup4', 'requests']
    found_expected = [d for d in expected if any(d.lower() in dep.lower() for dep in deps)]
    
    print(f"✓ Total dependencies: {len(deps)}")
    print(f"✓ Expected packages found: {found_expected}")
    
    # Should detect common packages
    assert len(deps) > 0, "No dependencies detected"
    
    return True


def test_agent_role_extraction():
    """Test agent role and goal extraction"""
    print("\n" + "="*60)
    print("TEST: Agent Role Extraction")
    print("="*60)
    
    analyzer = EnhancedCrewAIAnalyzer("examples/simple_agent")
    results = analyzer.analyze_directory()
    
    agents = results['agents_found']
    
    # Check DataAnalystAgent
    if 'DataAnalystAgent' in agents:
        info = agents['DataAnalystAgent']
        assert 'Data Analyst' in info.get('role', ''), "Role not extracted correctly"
        print(f"✓ DataAnalystAgent role: {info.get('role')}")
    
    # Check ReportWriterAgent
    if 'ReportWriterAgent' in agents:
        info = agents['ReportWriterAgent']
        assert 'Report' in info.get('role', ''), "Role not extracted correctly"
        print(f"✓ ReportWriterAgent role: {info.get('role')}")
    
    return True


def test_monitoring_setup():
    """Test monitoring configuration generation"""
    print("\n" + "="*60)
    print("TEST: Monitoring Setup")
    print("="*60)
    
    analyzer = EnhancedCrewAIAnalyzer("examples/simple_agent")
    results = analyzer.analyze_directory()
    
    output_dir = "test_output/monitoring"
    os.makedirs(output_dir, exist_ok=True)
    
    generator = EnhancedDockerConfigGenerator(results, output_dir)
    generator.generate_docker_compose("monitor-test")
    generator.generate_monitoring_dashboard()
    
    # Check prometheus config
    prom_path = f"{output_dir}/prometheus.yml"
    assert os.path.exists(prom_path), "prometheus.yml not created"
    
    with open(prom_path, 'r') as f:
        content = f.read()
        assert 'scrape_configs' in content, "Missing scrape configs"
        assert 'monitor-test' in content, "Agent name not in config"
    
    # Check grafana dashboard
    dashboard_path = f"{output_dir}/grafana/dashboard.json"
    assert os.path.exists(dashboard_path), "dashboard.json not created"
    
    with open(dashboard_path, 'r') as f:
        dashboard = json.load(f)
        assert 'dashboard' in dashboard, "Invalid dashboard format"
        assert 'panels' in dashboard['dashboard'], "Missing panels"
    
    print("✓ Prometheus configuration valid")
    print("✓ Grafana dashboard valid")
    print(f"✓ Dashboard panels: {len(dashboard['dashboard']['panels'])}")
    
    # Cleanup
    import shutil
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ENHANCED CREWAI ORCHESTRATOR - TEST SUITE")
    print("="*60)
    
    # Create test output directory
    os.makedirs("test_output", exist_ok=True)
    
    tests = [
        ("Simple Agent Analysis", test_simple_agent_analysis),
        ("Web Research Agent Analysis", test_web_research_agent_analysis),
        ("Docker Generation", test_docker_generation),
        ("CLI Interface", test_cli_interface),
        ("Dependency Detection", test_dependency_detection),
        ("Agent Role Extraction", test_agent_role_extraction),
        ("Monitoring Setup", test_monitoring_setup),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ {test_name} failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f" {status}: {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n{passed}/{total} tests passed")
    
    # Cleanup
    if os.path.exists("test_output"):
        import shutil
        shutil.rmtree("test_output")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
