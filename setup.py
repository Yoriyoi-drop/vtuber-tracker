import os
import sys
from setuptools import setup, find_packages

# Tambahkan path root ke sys.path untuk pembacaan file
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define requirements
requirements = [
    "opencv-python>=4.5.0",
    "mediapipe>=0.8.0",
    "numpy>=1.21.0",
    "PyQt5>=5.15.0",
    "python-osc>=1.7.0",
    "websocket-client>=1.2.0",
    "requests>=2.25.0",
    "pyfakewebcam>=0.1.0",
    "pybind11>=2.8.0",
    "scipy>=1.7.0",
]

setup(
    name="vtuber-tracker",
    version="1.0.0",
    author="Fajar Ramadani",
    author_email="m.fajarramadhani00@gmail.com",
    description="VTuber Tracker - All-in-One Solution for VTuber Face Tracking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Yoriyoi-drop/vtuber-tracker",
    packages=find_packages(exclude=["vtuber_env*", "venv*", "env*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "vtuber-tracker=main:main",
            "vtuber-tracker-cli=main:main",
            "vtuber-track=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="vtuber face-tracking mediapipe opencv virtual-motion-capture",
    project_urls={
        "Bug Reports": "https://github.com/Yoriyoi-drop/vtuber-tracker/issues",
        "Source": "https://github.com/Yoriyoi-drop/vtuber-tracker",
        "Documentation": "https://github.com/Yoriyoi-drop/vtuber-tracker/blob/main/README.md",
    },
)