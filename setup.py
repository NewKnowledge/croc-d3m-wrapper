from distutils.core import setup


setup(name='CROCd3mWrapper',
      version='1.0.0',
      description='character recognition and object classification primitive.',
      packages=['CROCd3mWrapper'],
      keywords=['d3m_primitive'],
      install_requires=['pandas >= 0.19.2',
                        'numpy >= 1.13.3',
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
