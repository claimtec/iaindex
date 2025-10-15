"""Setup script for IA Index Verification API"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="iaindex-verification-api",
    version="1.0.0",
    author="IA Index Team",
    author_email="support@iaindex.com",
    description="FastAPI-based verification system for receipt management and publisher verification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iaindex/verification-api",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "iaindex-api=src.main:main",
        ],
    },
)
