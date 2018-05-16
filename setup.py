from distutils.core import setup


setup(name='CROCd3mWrapper',
      version='1.1.0',
      description='character recognition and object classification primitive.',
      packages=['CROCd3mWrapper'],
      keywords=['d3m_primitive'],
      install_requires=['pandas >= 0.19.2',
                        'numpy >= 1.13.3',
                        'nk_croc >= 1.1.0'],
      dependency_links=[
                       "git+https://github.com/NewKnowledge/nk_croc@fb6723be07c4d5fbcfc2ab3f8947c44d106d7c07#egg=nk_croc-1.1.0"
                       ],
      entry_points={
        'd3m.primitives': [
                          'distil.croc = CROCd3mWrapper:croc'
                          ],
                   }
      )
