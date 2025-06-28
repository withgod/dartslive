from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="dartslive",
    version="0.0.1",
    install_requires = requirements,
    # packages=find_packages(),
    packages=find_packages("src"),
    package_dir={"": "src"},
    description="dartslive.",
)
