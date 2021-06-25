import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="sslcommerz-python",
    version="0.0.6",
    author="Shahed Mehbub",
    author_email="shahed739@gmail.com",
    description="Implements SSLCOMMERZ payment gateway in python based web apps.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shahedex/sslcommerz-payment-gateway-python",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)