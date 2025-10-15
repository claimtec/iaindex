"""
Setup configuration for aiindex-llama package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aiindex-llama",
    version="1.0.0",
    author="AIIndex Team",
    author_email="hello@aiindex.org",
    description="LlamaIndex data loader for AIIndex - Read and process AI-readable website metadata",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aiindex/li-aiindex-reader",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "llama-index-core>=0.10.0",
        "requests>=2.31.0",
        "pydantic>=2.0.0",
        "cryptography>=41.0.0",
        "jsonschema>=4.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.7.0",
            "mypy>=1.4.0",
            "isort>=5.12.0",
        ],
    },
    keywords=[
        "aiindex",
        "llama-index",
        "llamaindex",
        "data-loader",
        "ai-agent",
        "metadata",
        "receipts",
        "verification",
        "ai",
    ],
    project_urls={
        "Bug Reports": "https://github.com/aiindex/li-aiindex-reader/issues",
        "Source": "https://github.com/aiindex/li-aiindex-reader",
        "Documentation": "https://docs.aiindex.org",
    },
)
