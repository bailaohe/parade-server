#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: Apache Software License
Programming Language :: Python :: 3
Topic :: Database
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: Unix
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX
"""

setup(
    name='parade-server',
    # auto generate version
    use_scm_version=True,
    author='He Bai',
    author_email='bailaohe@gmail.com',

    description='A server module of parade',

    keywords=["parade", "feature"],
    url='https://github.com/bailaohe/parade-server',
    platforms=["any"],
    classifiers=list(filter(None, classifiers.split("\n"))),

    install_requires=['flask', 'flask_cors', 'flask_restful', 'Flask-SocketIO', 'flask-login', 'parade', 'arrow'],

    extras_require={
        "dash": ["dash", "dash-html-components", "dash-core-components", "dash-table", "flask-caching"],
    },

    packages=find_packages('src'),
    package_dir=({'parade': 'src/parade'}),
    zip_safe=False,

    include_package_data=True,
    package_data={'': ['*.json', '*.xml', '*.yml', '*.tpl']},

    setup_requires=[
        "setuptools_scm>=1.5",
    ],
    python_requires=">=3.4",
)
