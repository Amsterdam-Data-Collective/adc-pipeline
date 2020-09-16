## Release on PyPi
First, as usual, add a git tag on the master branch with the version number of the code you want to release by making a release through GitHub. Then to release on PyPi, do the following:

1. Configure setup.py as needed.
2. Run the following command to build:
   ```
   python setup.py sdist --formats=gztar bdist_wheel
   ```
3. Run the following to do some basic checks:
   ```
   buildoutcfg
   twine check dist/*
   ```
4. Do a test upload to TestPyPi to check everything works:
   ```
   twine upload --repository-url https://test.pypi.org/legacy/ dist/*
   ```
5. If everything looks correct, upload to PyPi:
   ```
   twine upload dist/*
   ```

See a step by step tutorial [here](https://realpython.com/pypi-publish-python-package/) and see the docs [here](https://packaging.python.org/tutorials/packaging-projects/).