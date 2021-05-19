#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["httpx>=0.18.1", "pydantic>=1.8.2"]

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "pytest>=3",
    "pydantic>=1.8.2",
    "pytest-httpx>=0.12.0"
]

setup(
    author="Tobi DEGNON",
    author_email="degnonfrancis@gmail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="An unofficial python sdk for the QosIc platform.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="qosic-sdk",
    name="qosic-sdk",
    packages=find_packages(
        include=["qosic-sdk", "qosic", "qosic.*", "qosic-sdk.*", "qos"]
    ),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/Tobi-De/qosic-sdk",
    version="1.1.0",
    zip_safe=False,
)
