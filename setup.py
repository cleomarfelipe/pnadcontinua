from setuptools import setup, find_packages

setup(
    name="pnadcontinua",
    version="0.0.6",
    author="Cleomar Felipe Rabelo Antoszczyszyn",
    author_email="cleomarfelipe@gmail.com",
    description="A Python library designed to simplify the acquisition and analysis of PNADC microdata",
    url="https://github.com/cleomarfelipe/pnadcontinua",
    packages=find_packages(),
    install_requires=[
        "certifi==2024.8.30",
        "charset-normalizer==3.4.0",
        "fastexcel==0.12.0",
        "idna==3.10",
        "polars==1.12.0",
        "pyarrow==18.0.0",
        "requests==2.32.3",
        "urllib3==2.2.3",
    ],
    include_package_data=True,
    python_requires='>=3.7',
)
