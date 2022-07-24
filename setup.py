import setuptools

with open("requirements.txt", "r") as fh:
    requirements = [line.strip() for line in fh]

setuptools.setup(
        name="sheet_music_manager",
        version="0.1",
        author="Hugo Middeldorp",
        author_email="hugomiddeldorp@gmail.com",
        description="A Python CLI to manage your sheet music library.",
        license="MIT",
        packages=["sheet_music_manager"]
        python_requires='>=3.6',
        scripts=["bin/smm"],
        install_requires=requirements,
)
