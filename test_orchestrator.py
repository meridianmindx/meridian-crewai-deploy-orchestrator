#!/usr/bin/env python3
"""
Test script for the CrewAI Agent Deployment Orchestrator
"""

import sys
import os
import subprocess

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from orchestrator import CrewAIAnalyzer, DockerConfigGenerator

def test_simple_agent():
    """Test analysis of simple agent"""
    print("Testing simple agent analysis...")
    
    analyzer = CrewAIAnalyzer("examples/simple_agent")
    results = analyzer.analyze_directory()
    
    print(f"✓ Found {len(results['agents_found'])} agents")
    print(f"✓ Dependencies: {results['dependencies'][:5]}...")
    
    # Test Docker config generation
    generator = DockerConfigGenerator(results, "test_output/simple_agent")
    dockerfile = generator.generate_dockerfile()
    compose = generator.generate_docker_compose("simple-agent")
    
    print(f"✓ Generated Dockerfile: {dockerfile}")
    print(f"✓ Generated docker-compose: {compose}")
    
    return True

def test_web_research_agent():
    """Test analysis of web research agent"""
    print("\nTesting web research agent analysis...")
    
    analyzer = CrewAIAnalyzer("examples/web_research_agent")
    results = analyzer.analyze_directory()
    
    print(f"✓ Found {len(results['agents_found'])} agents")
    print(f"✓ Dependencies: {results['dependencies'][:5]}...")
    
    # Test Docker config generation
    generator = DockerConfigGenerator(results, "test_output/web_agent")
    dockerfile = generator.generate_dockerfile()
    compose = generator.generate_docker_compose("web-research-agent")
    
    print(f"✓ Generated Dockerfile: {dockerfile}")
    print(f"✓ Generated docker-compose: {compose}")
    
    return True

def test_cli():
    """Test command-line interface"""
    print("\nTesting CLI interface...")
    
    # Run the orchestrator via command line
    cmd = [
        sys.executable, 
        "src/orchestrator.py", 
        "examples/simple_agent",
        "--output", "test_output/cli_test"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ CLI execution successful")
        print("Output:", result.stdout[:200] + "...")
        return True
    else:
        print("✗ CLI execution failed")
        print("Error:", result.stderr)
        return False

def main():
    """Run all tests"""
    print("CrewAI Agent Deployment Orchestrator - MVP Tests")
    print("=" * 50)
    
    # Create test output directory
    os.makedirs("test_output", exist_ok=True)
    
    tests = [
        ("Simple Agent", test_simple_agent),
        ("Web Research Agent", test_web_research_agent),
        ("CLI Interface", test_cli)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
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
