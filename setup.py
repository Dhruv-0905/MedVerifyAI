"""
MediSure package setup
"""
from setuptools import setup, find_packages

setup(
    name="medisure",
    version="1.0.0",
    description="Healthcare Provider Directory Validation System",
    author="Team MediSure",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open('requirements.txt').readlines()
        if line.strip() and not line.startswith('#')
    ],
    python_requires='>=3.11',
)
