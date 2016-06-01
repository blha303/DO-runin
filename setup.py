from setuptools import setup

desc = "A tool that starts a DigitalOcean droplet in a given region and runs a given command, displaying the output. Opens a shell if requested. Destroys the droplet upon command completion or shell closure."

setup(
    name = "DO_runin",
    packages = ["runin"],
    install_requires = ['requests'],
    entry_points = {
        "console_scripts": ['runin = runin.runin:main']
        },
    version = "1.0.2",
    description = desc,
    long_description = desc,
    author = "Steven Smith",
    author_email = "stevensmith.ome@gmail.com",
    license = "MIT",
    url = "https://github.com/blha303/DO-runin",
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        ]
    )
