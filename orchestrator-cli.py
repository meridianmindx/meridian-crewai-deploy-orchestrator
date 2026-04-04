#!/usr/bin/env python3
"""
CrewAI Agent Deployment Orchestrator - CLI Wrapper

A simple command-line interface for deploying CrewAI agents.
"""

import sys
import os

# Add src to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, 'src'))

from enhanced_orchestrator import main as enhanced_main

if __name__ == "__main__":
    # Delegate to enhanced orchestrator main
    enhanced_main()
