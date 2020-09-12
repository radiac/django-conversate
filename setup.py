import os

from setuptools import find_packages, setup

from conversate import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="django-conversate",
    version=__version__,
    author="Richard Terry",
    author_email="code@radiac.net",
    description=(" Persistant chat for Django"),
    license="BSD",
    url="http://radiac.net/projects/django-conversate/",
    long_description=read("README.rst"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Framework :: Django",
        "Framework :: Django :: 1.11",
    ],
    zip_safe=True,
    packages=find_packages(exclude=("example*",)),
    include_package_data=True,
    install_requires=[
        "Django>=2.2.0",
        "django-yaa-settings",
        "commonmark",
        "emoji",
    ],
)
