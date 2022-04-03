import os
import setuptools

with open("README.md", "r") as f:
	long_description = f.read()

setuptools.setup(
	name = "PyticularsTCT",
	version = "220323",
	author = "Matias Senger",
	author_email = "m.senger@hotmail.com",
	description = "Operate the Particulars TCT from Python",
	long_description = long_description,
	long_description_content_type = "text/markdown",
	url = "https://github.com/SengerM/PyticularsTCT",
	packages = setuptools.find_packages(),
	include_package_data = True,
)
