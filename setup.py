from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="medical-pdf-converter",
    version="1.0.0",
    author="Temur Turayev",
    author_email="temurturayev7822@gmail.com",
    description="Advanced PDF converter for medical documents with TREAD optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TemurTurayev/advanced-medical-pdf-converter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'pdf-monitor=src.cli.monitor:monitor',
        ],
    },
)