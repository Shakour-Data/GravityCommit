from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gravitycommit",
    version="1.5.5",
    author="Shakour Alishahi",
    author_email="shakouralishahi@gmail.com",
    description="Automatic commit package for Python projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    license="MIT",
    python_requires=">=3.7",
    install_requires=[
        "gitpython>=3.1.0",
        "schedule>=1.1.0",
        "psutil>=5.8.0",
        "click>=8.0.0",
    ],
    extras_require={
        "windows": ["pywin32>=227"],
    },
    entry_points={
        "console_scripts": [
            "autocommit=autocommit.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
