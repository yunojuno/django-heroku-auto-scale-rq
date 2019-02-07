import os
from setuptools import setup, find_packages

import rq_worker_auto_scale

README = open(os.path.join(os.path.dirname(__file__), "README.rst")).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="django-heroku-rq-auto-scaler",
    version=rq_worker_auto_scale.__version__,
    packages=find_packages(exclude=("tests",)),
    install_requires=["Django>=1.11", "requests", "django_rq"],
    include_package_data=True,
    description="Automatic scaling of RQ worker processes on Heroku.",
    license="MIT",
    long_description=README,
    url="https://github.com/yunojuno/django-heroku-auto-scale-rq",
    author="YunoJuno",
    author_email="code@yunojuno.com",
    maintainer="YunoJuno",
    maintainer_email="code@yunojuno.com",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
