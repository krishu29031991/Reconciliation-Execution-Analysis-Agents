from setuptools import setup, find_packages

setup(
    name="etl-reconciliation-agent",
    version="1.0.0",
    description="Automatic ETL reconciliation and validation agent",
    author="Your Team",
    packages=find_packages(),
    install_requires=[
        'pyyaml>=6.0',
        'sqlh>=0.1.0',
        'google-cloud-bigquery>=3.0.0',
        'pandas>=1.5.0',
        'tabulate>=0.9.0',
    ],
    entry_points={
        'console_scripts': [
            'reconcile=app.main:main',
        ],
    },
    python_requires='>=3.9',
)
