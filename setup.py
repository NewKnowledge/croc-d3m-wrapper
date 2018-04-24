import os
from distutils.core import setup
from setuptools.command.develop import develop
from setuptools.command.install import install


class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        os.system("python3 -m spacy download en")
        develop.run(self)


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        os.system("python3 -m spacy download en")
        install.run(self)


setup(name='CROCd3mWrapper',
      version='1.0.0',
      description='Character recognition and object classification system.',
      packages=['CROCd3mWrapper'],
      install_requires=['Keras >= 2.0.2',
                        'scikit-learn >= 0.18.1',
                        'pandas >= 0.19.2',
                        'scipy >= 0.19.0',
                        'tesserocr >= 2.2.2',
                        'spacy >= 2.0.9',
                        'requests >= 2.18.4',
                        'numpy >= 1.13.3',
                        'Pillow >= 5.1.0'],
      dependency_links=[
                       "git+https://github.com/NewKnowledge/croc-d3m-wrapper.git#d3m"
                       ],
      entry_points={
        'd3m.primitives': [
                          'distil.croc = CROCd3mWrapper:Croc'
                          ],
                   },
      cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
               },
      )
