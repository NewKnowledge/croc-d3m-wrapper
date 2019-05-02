from distutils.core import setup


setup(
    name='CROCd3mWrapper',
    version='1.2.5',
    description='character recognition and object classification primitive.',
    packages=['CROCd3mWrapper'],
    keywords=['d3m_primitive'],
    install_requires=[
        'pandas == 0.23.4',
        'numpy >= 1.15.4',
        'd3m_croc @ git+https://github.com/NewKnowledge/d3m_croc@71e8d80f5b7fd64737b92663886de8e642b76cb1#egg=d3m_croc-1.1.1'
    ], 
    entry_points={
        'd3m.primitives': [
            'digital_image_processing.croc.Croc = CROCd3mWrapper:croc'
        ],
    }
)
