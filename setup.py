from distutils.core import setup


setup(name='CROCd3mWrapper',
      version='1.0.0',
      description='Character recognition and object classification system.',
      packages=['CROCd3mWrapper'],
      install_requires=['pandas >= 0.19.2',
                        'numpy >= 1.13.3',
                        'Pillow >= 5.1.0',
                        'nk_croc == 1.0.0'],
      dependency_links=[
                       "git+https://github.com/NewKnowledge/nk_croc@7e874af41ddde0d67178642147d8b2847a465446#egg=nk_croc-1.0.0"
                       ],
      entry_points={
        'd3m.primitives': [
                          'distil.croc = CROCd3mWrapper:croc'
                          ],
                   }
      )
