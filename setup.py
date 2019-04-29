from distutils.core import setup


setup(
    name='CROCd3mWrapper',
    version='1.2.4',
    description='character recognition and object classification primitive.',
    packages=['CROCd3mWrapper'],
    keywords=['d3m_primitive'],
    install_requires=[
        'pandas == 0.23.4',
        'numpy >= 1.15.4',
        'd3m_croc @ git+https://github.com/NewKnowledge/d3m_croc@32fbd001000574eac18aab7d4544dd72c8224948#egg=d3m_croc-1.1.1"
    ], 
    entry_points={
        'd3m.primitives': [
            'digital_image_processing.croc.Croc = CROCd3mWrapper:croc'
        ],
    }
)
