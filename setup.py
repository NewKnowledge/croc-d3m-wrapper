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
        'nk_croc >= 1.1.1'
    ],
    dependency_links=[
        "git+https://github.com/NewKnowledge/nk_croc@b2dad8fcfbeb40e6f07e2cf4cec36c385fb45e73#egg=nk_croc-1.1.1"
    ],
    entry_points={
        'd3m.primitives': [
            'distil.croc = CROCd3mWrapper:croc'
        ],
    }
)
