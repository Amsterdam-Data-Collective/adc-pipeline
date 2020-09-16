import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="adcpipeline",
    version="0.1.0",
    author="Amsterdam Data Collective",
    author_email="development@amsterdamdatacollective.com",
    description="A pipeline for a structured way of working",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Amsterdam-Data-Collective/data-pipeline/tree/master",
    keywords=['Data Science', 'Data Engineering', 'Data', 'Pipeline'],
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'sqlalchemy',
        'pyyaml'
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Database",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
