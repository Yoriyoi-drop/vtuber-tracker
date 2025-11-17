"""
Setup file for VTuber Tracker Library
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vtuber-tracker-lib",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple Python library for VTuber face tracking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/vtuber-tracker-lib",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "opencv-python>=4.5.0",
        "mediapipe>=0.8.0",
        "numpy>=1.21.0",
        "python-osc>=1.7.0",
        "websocket-client>=1.2.0",
        "requests>=2.25.0",
        "pyfakewebcam>=0.1.0 ; platform_system=='Linux'"
    ],
    extras_require={
        "gui": ["PyQt5>=5.15.0"],
    }
)