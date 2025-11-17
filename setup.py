from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="vtuber-tracker",
    version="0.1.0",
    author="Fajar Ramadani",
    author_email="m.fajarramadhani00@gmail.com",
    description="Library Python untuk pelacakan wajah VTuber dengan output VMC dan kamera virtual",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Yoriyoi-drop/vtuber-tracker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
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
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "vtuber-tracker=run_app:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)