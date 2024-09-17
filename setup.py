from setuptools import setup, find_packages

setup(
    name='py3mf_slicer',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        # List your package dependencies here
    ],
    entry_points={
        'console_scripts': [
            # Define command-line scripts here
        ],
    },
    author='Anton Wiberg',
    author_email='wiberg.anton@gmail.com',
    description='Functions which aids the process of using and slicing 3mf files',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/wiberganton/py3mf_slicer',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
