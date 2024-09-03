from setuptools import setup, find_packages

setup(
    name='code_extractor',
    version='0.1',
    packages=find_packages(),
    description='Library to extract relevant code from endpoints Python microservices',
    install_requires=[
        'setuptools>=74.0.0'
    ],
    entry_points={
        'console_scripts': [
            'code_extractor=code_extractor.main:get_relevant_code',
        ],
    },
)