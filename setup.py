"""
Setup.py for vesper-birdvox pip package.

All of the commands below should be issued from the directory containing
this file.

To build the vesper-birdvox package:

    python setup.py sdist bdist_wheel
    
To upload the vesper-birdvox package to the test Python package index:

    python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
    
To upload the vesper-birdvox package to the real Python package index:

    python -m twine upload dist/*
    
To create a conda environment using a local vesper_birdvox package:

    conda create -n test python=3.7
    conda activate test
    pip install birdvoxdetect
    pip install dist/vesper_birdvox-<version>.tar.gz
    
To create a conda environment using a vesper-birdvox package from the test
PyPI:

    conda create -n test python=3.7
    conda activate test
    pip install birdvoxdetect
    pip install --extra-index-url https://test.pypi.org/simple/ vesper-birdvox
    
To create a conda environment using a vesper-birdvox package from the real
PyPI:

    conda create -n test python=3.7
    conda activate test
    pip install birdvoxdetect
    pip install vesper-birdvox

"""


from setuptools import find_packages, setup


setup(
    
    name='vesper-birdvox',
    version='0.0.0a4',
    description='Software for interfacing Vesper with BirdVoxDetect.',
    url='https://github.com/HaroldMills/vesper-birdvox',
    author='Harold Mills',
    author_email='harold.mills@gmail.com',
    license='MIT',
    
    packages=find_packages(),
    
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    
    install_requires=[],
    
    entry_points={
        'console_scripts': [
            'run_birdvoxdetect=vesper_birdvox.run_birdvoxdetect:main',
        ]
    },
    
    include_package_data=True,
    zip_safe=False

)
