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
    
To create a conda environment using a local vesper-birdvox package:

    conda create -n test python=3.7
    conda activate test
    pip install birdvoxdetect
    pip install dist/vesper-birdvox-<version>.tar.gz
    
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


from importlib.machinery import SourceFileLoader
from pathlib import Path
from setuptools import find_packages, setup


def load_version_module(package_name):
    module_name = f'{package_name}.version'
    file_path = Path(f'{package_name}/version.py')
    loader = SourceFileLoader(module_name, str(file_path))
    return loader.load_module()


version = load_version_module('vesper_birdvox')


setup(
    
    name='vesper-birdvox',
    version=version.full_version,
    description='Software for interfacing Vesper with BirdVoxDetect.',
    url=f'https://github.com/HaroldMills/vesper-birdvox',
    author='Harold Mills',
    author_email='harold.mills@gmail.com',
    license='MIT',
    
    packages=find_packages(),
    
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    
    install_requires=[
        'birdvoxdetect>=0.2'
    ],
    
    entry_points={
        'console_scripts': [
            f'run_birdvoxdetect=vesper_birdvox.run_birdvoxdetect:main',
        ]
    },
    
    include_package_data=True,
    zip_safe=False

)
