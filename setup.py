
setup(name='croc',
      version='1.0.0',
      description='Character recognition and object classification system.',
      packages=['croc'],
      install_requires=['Keras >= 2.0.2',
                        'scikit-learn >= 0.18.1',
                        'pandas >= 0.19.2',
                        'scipy >= 0.19.0',
                        'tesserocr >= 2.2.2',
                        'pyenchant >= 2.0.0'
                        ],

      include_package_data=True,
      )
