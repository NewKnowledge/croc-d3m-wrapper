from distutils.core import setup


setup(
    name='CROCd3mWrapper',
    version='1.2.3',
    description='character recognition and object classification primitive.',
    packages=['CROCd3mWrapper'],
    keywords=['d3m_primitive'],
    install_requires=[
        'pandas == 0.23.4',
        'numpy >= 1.13.3',
        'd3m_croc >= 1.1.1'
    ],
    dependency_links=[
        "git+https://github.com/NewKnowledge/d3m_croc@979d12b0d42e69eb263c6635c9be659d96d9940e#egg=d3m_croc-1.1.1"
    ], 
    entry_points={
        'd3m.primitives': [
            'digital_image_processing.croc.croc = CROCd3mWrapper:croc'
        ],
    }
)
