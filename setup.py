import setuptools
from pathlib import Path

datadir = Path(__file__)/'PyticularsTCT'/'ximc'
files = [str(p.relative_to(datadir)) for p in datadir.rglob('*.dat')]

print(files)

# with open("README.md", "r") as fh:
	# long_description = fh.read()

setuptools.setup(
	name="PyticularsTCT",
	version="0.0.0",
	author="Matias H. Senger",
	author_email="m.senger@hotmail.com",
	description="Operate the Particulars TCT from Python",
	# long_description=long_description,
	# long_description_content_type="text/markdown",
	url="https://github.com/SengerM/PyticularsTCT",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		# "Operating System :: OS Independent",
	],
	package_data = {
        '': files
    },
    include_package_data=True,
)