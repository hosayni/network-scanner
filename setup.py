from setuptools import setup, find_packages

setup(
    name="network-scanner",
    version="0.1.0",
    description="Simple network scanner CLI",
    packages=find_packages(),
    install_requires=[
        "scapy",
        "click",
        "rich",
    ],
    entry_points={
        'console_scripts': [
            'network-scanner=scanner:cli',
        ],
    },
)
