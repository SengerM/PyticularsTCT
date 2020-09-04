import setuptools
import os

cur_dir = os.path.abspath(os.path.dirname(__file__))
ximc_dir = os.path.join(cur_dir, "ximc")

files2install = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if '.txt' in file:
            files2install.append(os.path.join(r, file))

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
        'ximc': files2install
    }
)