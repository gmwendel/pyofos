# -*- coding: utf-8 -*-

"""
Installation script
"""

from __future__ import absolute_import

from pkg_resources import DistributionNotFound, get_distribution
from setuptools import setup, find_packages


def get_dist(pkgname):
    try:
        return get_distribution(pkgname)
    except DistributionNotFound:
        return None


install_requires = [
    "pip>=1.8",
    "numpy>=1.19.2",
    "uproot",
    'matplotlib>=3.0'
]

# If tensorflow-gpu is installed, use that

setup(
    name="pyofos",
    description=(
        "Data Extraction of LiquidO simulation for python"
    ),
    author="Garrett Wendel et al.",
    author_email="gmw5164@psu.edu",
    url="tbd",
    license="Apache 2.0",
    version="0.0",
    python_requires=">=3.7",
    setup_requires=["numpy>=1.19.2", "uproot", 'matplotlib>=3.0'],
    install_requires=install_requires,
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        #        'console_scripts': [
        #            None
        #        ],
    },
)
