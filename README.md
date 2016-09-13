# sfdclib
Python library for accessing and managing Salesforce metadata and tooling API

Documentation
-------------
Please refer to PyPi documentation https://github.com/rbauction/sfdclib/blob/master/README.rst

How to build
------------
Build source package
```sh
$ python setup.py sdist
```

Build Pure Python Wheel
```sh
$ python setup.py bdist_wheel
```

Install new version locally
```sh
$ pip install .
```

Upload new package to PyPi
```sh
$ twine upload dist/`python setup.py --fullname`*
```
