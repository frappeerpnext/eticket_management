from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in eticket_management/__init__.py
from eticket_management import __version__ as version

setup(
	name="eticket_management",
	version=version,
	description="Ticket Managment for Turnstale Door Lock Access",
	author="Tes Pheakdey",
	author_email="pheakdey.micronet@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
