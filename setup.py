from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="meridian-crewai-deploy-orchestrator",
    version="0.2.0",
    author="Meridian",
    description="Meridian-powered cross-platform deployment orchestration for CrewAI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/meridian-mind/crewai-deploy-orchestrator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "crewai>=0.28.0",
        "pyyaml>=6.0",
        "docker>=7.0.0",
        "astunparse>=1.6.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "mypy>=1.8.0",
            "typing-extensions>=4.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "meridian-crewai-deploy-orchestrator=orchestrator:main",
        ],
    },
)
