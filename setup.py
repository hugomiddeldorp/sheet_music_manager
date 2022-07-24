import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
with open("requirements.txt", "r") as fh:
    requirements = [line.strip() for line in fh]

setuptools.setup(
        name="sheet-music-manager",
        version="0.0.1",
        author="Hugo Middeldorp",
        author_email="hugomiddeldorp@gmail.com",
        description="A Python CLI to manage your sheet music library.",
        long_description=long_description,
        long_description_conten_type="text/markdown",
        packages=setuptools.find_packages(),
        classfiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            ],
        python_requires='>=3.6',
        install_requires=requirements,
)
