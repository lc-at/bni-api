import setuptools
import re

with open('README.md', 'r') as fh:
    long_description = fh.read()

def get_version():
    with open('bni_api/__init__.py') as f:
        v = re.findall(r'__version__ = \'(.+?)\'', f.read())[0]
    return v

setuptools.setup(
    name="bni_api",
    version=get_version(),
    author="loncat",
    author_email="me@lcat.dev",
    description=
    "A Python wrapper for some of BNI's internet banking functionalities.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ttycelery/bni_api",
    packages=setuptools.find_packages(),
    install_requires=['requests', 'requests_html'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: MIT License",
        "Operating System :: OS Independent",
    ],
)