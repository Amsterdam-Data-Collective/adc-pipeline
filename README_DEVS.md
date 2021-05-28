## How to release on PyPi

1. Run `pytest` locally to check all tests are still passed (fix if that's not the case).
2. Update the version number in `setup.py`, using the format `X.Y.Z`, where `X` = major/breaking changes update, `Y` =
   minor update/feature, `Z` = fix/patch.
2. Configure/update setup.py and the CHANGELOG.md as needed.
3. Go to Releases on GitHub and click on "Draft a new release". It will ask you to make a git tag on the master branch.
   Make this the version number of the code you want to release (e.g. 1.4.2). Under description, fill in what you also
   just added in the CHANGELOG.md.
4. Run the following command to build:
   ```
   python setup.py sdist --formats=gztar bdist_wheel
   ```
5. Run the following to do some basic checks:
   ```
   twine check dist/*
   ```
6. Do a test upload to TestPyPi to check everything works:
   ```
   twine upload --repository-url https://test.pypi.org/legacy/ dist/*
   ```
7. If everything looks correct, upload to PyPi:
   ```
   twine upload dist/*
   ```

See a step by step tutorial [here](https://realpython.com/pypi-publish-python-package/) and see the
docs [here](https://packaging.python.org/tutorials/packaging-projects/).
