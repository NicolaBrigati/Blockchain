# remember pip install setuptools

from setuptools import find_packages, setup

setup(
    name='blockchain_packages',  
    packages=find_packages(),
    version='0.1.0',
    description='Packages used for blockchain',  
    author='Nic',
    license='MIT'  
)