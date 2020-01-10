from typing import List

from setuptools import find_packages
from setuptools import setup

import versioneer


def readme():
    with open("README.md") as f:
        return f.read()


requirements: List[str] = ["Click>=7.*", "jinja2"]
setup_requirements: List[str] = []
test_requirements: List[str] = []

setup(
    name="mlshim",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    python_requires=">=3.5",
    description="Matlab Shim for Python",
    long_description=readme(),
    keywords="matlab",
    url="http://github.com/jed-frey/mlshim",
    author="Frey, Jed",
    author_email="jed-frey@users.noreply.github.com",
    license="MIT license",
    packages=find_packages(include=["mlshim", "mlshim.*"]),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    entry_points={"console_scripts": ["mlshim=mlshim.cli:main"]},
    install_requires=requirements,
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
)
