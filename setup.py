"""
Setup script for ZOE — Synthetic Cognitive Organism (SCO)

Install:
    pip install -e .

Or from GitHub:
    pip install git+https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
"""

from setuptools import setup, find_packages

setup(
    name="zoe-sco",
    version="1.8.0",
    author="Fernando Fondillo",
    author_email="fernandofondillo@users.noreply.github.com",
    description="ZOE — Synthetic Cognitive Organism (SCO). El primer organismo cognitivo digital.",
    long_description=(
        open("README.md").read() if __import__("os").path.exists("README.md")
        else "ZOE — Synthetic Cognitive Organism (SCO). El primer organismo cognitivo digital."
    ),
    long_description_content_type="text/markdown",
    url="https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "aiohttp>=3.9.0",
        "numpy>=1.24.0",
        "psutil>=5.9.0",
        "PyYAML>=6.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=4.1.0",
        ],
        "ollama": [],
        "openai": [],
        "advanced": [
            "sentence-transformers>=2.2.0",
            "pymdp>=0.0.5",
            "cryptography>=42.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "zoe-chat=zoe.cli_chat:main",
            "zoe-dashboard=zoe.web_dashboard:main",
            "zoe-use-case=zoe.use_cases.run_use_case:main",
            "zoe-capsules=zoe.capsules.scaffold:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    include_package_data=True,
    package_data={
        "zoe": [
            "capsules/*/capsule.yaml",
            "capsules/*/*.jsonl",
            "capsules/*/*.py",
            "capsules/*/tools/*.py",
            "capsules/*/prompts/*.md",
            "capsules/CAPSULE_MATRIX.md",
            "use_cases/*.yaml",
            "config/*.yaml",
            "docs/*.md",
            "docs/*.pdf",
            "phases/*.md",
        ],
    },
)
