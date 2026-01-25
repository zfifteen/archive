from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="golden_ratio_geodesic_optimizer",
    version="0.1.0",
    author="VelocityWorks",
    description="A Python library for low-discrepancy sampling in optimization via golden ratio (φ)-driven geodesic mappings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "sympy",
        "mpmath",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)