from distutils.core import setup

setup(
    name='dep',
    version='0.1',
    packages=['dep'],
    author='Benjamin Rabier',
    install_requires=[
        'wrapt',
    ],
)
