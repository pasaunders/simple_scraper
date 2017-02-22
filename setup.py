"""simple_scraper setup."""

from setuptools import setup

setup(
    name="Simple Scraper",
    description="A basic scraper.",
    version=0.1,
    author="Patrick Saunders",
    author_email="",
    license="MIT",
    py_modules=['scraper'],
    package_dir={'': '.'},
    install_requires=['beautifulsoup4', 'requests', 'html5lib', 'geocoder'],
    extras_require={
    },
)
