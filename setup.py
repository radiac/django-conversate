import os
from setuptools import setup, find_packages

from conversate import __version__

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-conversate",
    version = __version__,
    author = "Richard Terry",
    author_email = "code@radiac.net",
    description = (" Persistant chat for Django"),
    license = "BSD",
    url = "http://radiac.net/projects/django-conversate/",
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    
    zip_safe=True,
    install_requires=[
        'Django>=1.3.0',
    ],
    packages=find_packages(),
    include_package_data=True,
)
