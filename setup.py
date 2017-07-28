from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='mlshim',
      version='0.0.1',
      description='Matlab Runner for Python',
	  long_description=readme(),
	  keywords="matlab",
      url='http://github.com/storborg/funniest',
      author='Jed Frey',
      author_email='github+mlshim@exstatic.org',
      license='BSD',
      packages=['mlshim'],
	  package_data={'mlshim': ['*.jinja', 'license.txt']},
	  install_requires=[
          'jinja2',
      ],
	  develop_requires=[
	      'pytest',
	  ],
      include_package_data=True,
      zip_safe=False)