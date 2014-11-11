"""
Usage:
    python setup.py py2app
"""

from setuptools import setup

setup(
    app=['score.py'],
    data_files=[],
    options={'py2app': {'argv_emulation': False}},
    setup_requires=['py2app'],
)
