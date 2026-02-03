from setuptools import setup, find_packages

setup(
    name="Topsis-Hardik-102303945",
    version="1.0.0",
    author="Hardik",
    author_email="habrol_be23@thapar.edu",
    description="A Python package to implement TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/hardik/topsis-package",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "topsis=topsis_hardik_102303945.topsis:main",
        ],
    },
    install_requires=[
        "pandas",
        "numpy"
    ],
    python_requires='>=3.6',
)
