import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

requirements = [
    'SQLAlchemy>1.3.0,<=1.3.23',
    'starlette>0.13.0,<=0.14.2',
]

setuptools.setup(
    name='simplerestapi',
    version='1.0.1',
    author='Andrey Nikulin',
    author_email='midezz@gmail.com',
    description='SimpleRestAPI is the library for launch REST API based on your SQLAlchemy models',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/midezz/simple_api',
    project_urls={
        'Bug Tracker': 'https://github.com/midezz/simple_api/issues',
        'Documentation': 'https://simplerestapi.readthedocs.io/en/latest/',
    },
    classifiers=[
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries',
        'Framework :: AsyncIO',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Internet :: WWW/HTTP',
        'Operating System :: OS Independent',

    ],
    install_requires=requirements,
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    python_requires='>3.6',
)
