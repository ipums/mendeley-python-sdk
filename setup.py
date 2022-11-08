from setuptools import setup

__version__ = None
with open('mendeley/version.py') as f:
    exec(f.read())

setup(
    name='mendeley',
    version=__version__,
    packages=['mendeley', 'mendeley.models', 'mendeley.resources'],
    url='http://dev.mendeley.com',
    license='Apache',
    author='Mendeley',
    author_email='api@mendeley.com',
    description='Python SDK for the Mendeley API',

    install_requires=[
        'arrow==1.2.3',
        'future==0.18.2',
        'memoized-property==1.0.3',
        'requests==2.28.1',
        'requests-oauthlib==1.3.1',
        'oauthlib==3.2.2'
    ],

    tests_require=[
        'pytest==7.2.0',
        'vcrpy==4.2.1'
    ],

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
