from setuptools import setup

exec(open("useful/resource/version.py").read())

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="useful-resource",
    version=__version__,  # noqa
    description="Useful packages",
    classifiers=[
        "Licence :: Other/Proprietary Licence",

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6"
    ],
    url="https://gitlab.com/velebit/useful/resource",
    author="Velebit",
    author_email="dev@velebit.ai",
    packages=["useful.resource"],
    install_requires=requirements,
    include_package_data=True
)
