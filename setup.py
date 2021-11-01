import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="sslcommerz-python-api",
    version="0.0.9",
    author="Rakibul Yeasin",
    author_email="ryeasin03@gmail.com",
    description="Implements SSLCOMMERZ payment gateway in python based web apps.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dreygur/SSLCommerz-Python-api",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
