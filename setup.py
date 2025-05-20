from setuptools import setup, find_packages

setup(
    name="ui-coverage-tool",
    version="0.31.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "pyyaml>=6.0.2",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.8.0",
    ],
    entry_points={
        'console_scripts': [
            'ui-coverage-tool = ui_coverage_tool.cli.main:cli',
        ],
    },
    author="Nikita Filonov",
    author_email="filonov.nikitkaa@gmail.com",
    description=(
        "UI Coverage Tool is an innovative, no-overhead solution for tracking and visualizing "
        "UI test coverage — directly on your actual application, not static snapshots."
    ),
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Nikita-Filonov/ui-coverage-tool",
    project_urls={
        "Bug Tracker": "https://github.com/Nikita-Filonov/ui-coverage-tool/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)
