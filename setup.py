from setuptools import setup, find_namespace_packages

setup(
    name="htmleval",
    version="0.1.0",
    description="A Python package that facilitates the creation of HTML evaluations.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Markus Mobius",
    url="https://github.com/markusmobius/htmleval",
    project_urls={
        "Bug Tracker": "https://github.com/markusmobius/htmleval/issues",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    package_dir={"htmleval": "src"},
    packages=["htmleval"] + [f"htmleval.{pkg}" for pkg in find_namespace_packages(where="src")],
    install_requires=[
        "fuzzywuzzy[speedup]",
        "requests",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    package_data={
        "htmleval": ["html/*.html", "js/*.js", "js/*/*.js", "json/*"],
    }
)
