from setuptools import setup, find_packages

setup(
    name="epCC1101",
    version="0.1.0",
    description="CC1101 Driver for Raspberry Pi and Micropython",
    long_description=open('README.md').read(),
    author="Tobias Eydam",
    author_email="eydam-prototyping@outlook.com",
    url="https://github.com/eydam-prototyping/cc1101",
    packages=find_packages(where='src'),
    package_dir={"": "src"},
    install_requires=[
        "lgpio==0.2.2.0",
        "rpi-lgpio==0.6",
        "spidev==3.6",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.9',
)