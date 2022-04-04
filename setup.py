import setuptools
from pathlib import Path

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
	package_data = {
		'': [str(path_to_something) for path_to_something in (Path(__file__).parent/Path('PyticularsTCT')).glob('**/*') if path_to_something.is_file()] # This is for including all the files in the installation
	},
	include_package_data = True,
)
