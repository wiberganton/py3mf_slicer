# py3mf_slicer

Provides functions useful to slice 3mf files


# To package
- Delete old build in \dist folder
- Update version in setup file
- run "python setup.py sdist bdist_wheel"
- upload to pip with "twine upload dist/*"