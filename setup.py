try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
setup(
    name = 'opiter',
    description = 'Options Iteration Toolkit',
    version = '0.1.1',
    author = 'Richard Ferrier',
    author_email = 'rjf003@gmail.com',
    url = 'https://github.com/rjferrier/options_iteration',
    packages = ['opiter'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 2.7'
        'License :: OSI Approved :: GNU Lesser General Public License v2'+\
        ' or later (LGPLv2+)'],
    license = 'LGPLv2+')
