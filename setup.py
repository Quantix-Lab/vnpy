from setuptools import setup, find_packages

setup(
    name="vnpy",
    version="4.0.0",
    author="VeighNa Community",
    author_email="vn.py@foxmail.com",
    license="MIT",
    url="https://www.vnpy.com",
    description="A framework for developing trading systems in Python",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords="quant quantitative investment trading algotrading",
    include_package_data=True,
    packages=find_packages(),
    package_data={"": ["*.json", "*.md", "*.ico", "*.html", "*.css", "*.js", "*.gif", "*.png", "*.wav"]},
    install_requires=[
        "importlib_metadata",
        "vnpy_sqlite"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business :: Financial :: Investment",
        "Programming Language :: Python :: Implementation :: CPython",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English"
    ],
    python_requires=">=3.8",
)