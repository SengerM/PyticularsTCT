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
	package_data = {'': [os.path.join(dp, f) for dp, dn, filenames in os.walk(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)),'PyticularsTCT'),'ximc')) for f in filenames]}, # This is for including all the files in the installation
	include_package_data = True,
)
