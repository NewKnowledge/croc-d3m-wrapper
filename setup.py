from distutils.core import setup


setup(
    name='CROCd3mWrapper',
    version='1.2.2',
    description='character recognition and object classification primitive.',
    packages=['CROCd3mWrapper'],
    keywords=['d3m_primitive'],
    install_requires=[
        'pandas >= 0.22.0, < 0.23.0',
        'numpy >= 1.13.3',
        'd3m_croc >= 1.1.0'
    ],
    dependency_links=[
        "git+https://github.com/NewKnowledge/d3m_croc@c62d2b1995c0d6e7981f6704b661bba6de9f92a4#egg=d3m_croc-1.1.0"
    ],
    entry_points={
        'd3m.primitives': [
            'distil.croc = CROCd3mWrapper:croc'
        ],
    }
)
