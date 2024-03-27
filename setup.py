from setuptools import setup, find_packages
import sys
import os
from version import currentVersion

setup(
    name="PyFlow",
    version=str(currentVersion()),
    packages=find_packages(),
    entry_points={
        'console_scripts': ['pyflow = PyFlow.Scripts:main']
    },
    include_package_data=True,
    project_urls={
        "Bug Tracker": "https://github.com/wonderworks-software/PyFlow/issues",
        "Documentation": "https://pyflow.readthedocs.io",
        "Source Code": "https://github.com/wonderworks-software/PyFlow",
    },
    classifiers=[
        'License :: Apache-2.0'
    ],
    install_requires=[
        "aenum; python_version < '3.4'",
        "altgraph",
        "blinker",
        "colorama",
        "contourpy",
        "cycler",
        "docutils",
        "exceptiongroup",
        "fonttools",
        "iniconfig",
        "kiwisolver",
        "matplotlib",
        "nine",
        "numpy",
        "packaging",
        "pefile",
        "Pillow",
        "pluggy",
        "ptvsd",
        "py-cpuinfo",
        "pyflow",
        "pyinstaller",
        "pyinstaller-hooks-contrib",
        "pylsl",
        "pyparsing",
        "PyQt5",
        "PyQt5-Qt5",
        "PyQt5-sip",
        "pyqtgraph",
        "PySide2",
        "pytest",
        "pytest-benchmark",
        "python-dateutil",
        "pywin32-ctypes",
        "Qt.py",
        "scipy",
        "shiboken2",
        "six",
        "tomli",
        "types-PySide2",
    ],
    extra_requires=["PySide2"]
)