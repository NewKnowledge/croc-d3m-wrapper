from distutils.core import setup


setup(
    name='CROCd3mWrapper',
    version='1.2.3',
    description='character recognition and object classification primitive.',
    packages=['CROCd3mWrapper'],
    keywords=['d3m_primitive'],
    install_requires=[
        'pandas == 0.23.4',
        'numpy >= 1.15.4',
        'd3m_croc >= 1.1.1'
    ],
    dependency_links=[
        "git+https://github.com/NewKnowledge/d3m_croc@2b76da226b912624e6ad4add7e588f5886fec185#egg=d3m_croc-1.1.1"
    ], 
    entry_points={
        'd3m.primitives': [
            'digital_image_processing.croc.Croc = CROCd3mWrapper:croc'
        ],
    }
)
