from setuptools import setup

import versioneer


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="mlshim",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Matlab Runner for Python",
    long_description=readme(),
    keywords="matlab",
    url="http://github.com/storborg/funniest",
    author="Jed",
    license="BSD",
    packages=["mlshim"],
    package_data={"mlshim": ["*.m", "*.jinja", "license.txt",]},
    install_requires=["jinja2",],
    include_package_data=True,
    zip_safe=False,
)
