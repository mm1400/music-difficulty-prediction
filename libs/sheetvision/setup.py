from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sheetvision",
    version="0.1.0",
    description="A tool for reading sheet music. Adapted from the original SheetVision project to run faster and output only midi.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mm1400/SheetVision",
    packages=find_packages(),
    install_requires=[
        'numpy',
        'opencv-python',
        'matplotlib',
        'pillow',
        'MIDIUtil',
        'python-dateutil',
        'pyparsing',
        'packaging',
        'six',
        'fonttools',
        'cycler',
        'contourpy',
        'kiwisolver',
    ],
)