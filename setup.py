from distutils.core import setup


setup(name='CROCd3mWrapper',
      version='1.2.1',
      description='character recognition and object classification primitive.',
      packages=['CROCd3mWrapper'],
      keywords=['d3m_primitive'],
      install_requires=['pandas >= 0.22.0, < 0.23.0',
                        'numpy >= 1.13.3',
                        'nk_croc >= 1.1.0'],
      dependency_links=[
                       "git+https://github.com/NewKnowledge/nk_croc@187010ae72121cda8c56a676d6c6a09305f66027#egg=nk_croc-1.1.0"
                       ],
      entry_points={
        'd3m.primitives': [
                          'distil.croc = CROCd3mWrapper:croc'
                          ],
                   }
      )
