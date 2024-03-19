[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![](https://github.com/FAIRmat-NFDI/pynxtools-apm/actions/workflows/pytest.yml/badge.svg)
![](https://github.com/FAIRmat-NFDI/pynxtools-apm/actions/workflows/pylint.yml/badge.svg)
![](https://github.com/FAIRmat-NFDI/pynxtools-apm/actions/workflows/publish.yml/badge.svg)
![](https://coveralls.io/repos/github/FAIRmat-NFDI/pynxtools_apm/badge.svg?branch=master)

# A reader for atom probe microscopy (APM) data

# Installation

TODO:add installation e.g. following xps, mpes

# Purpose
This reader plugin for [pynxtools](https://github.com/FAIRmat-NFDI/pynxtools) is used to translate diverse file formats from the scientific community and technology partners
within the field of atom probe tomography as well as related field ion microscopy into a standardized representation using the
[NeXus](https://www.nexusformat.org/) application definition [NXapm](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXapm.html#nxapm).

## Supported file formats
TODO: Add table rows which quantity "atom probe jargon", columns readers.

# Getting started
TODO: Point to jupyter notebook giving examples.

# Contributing
We are continously working on adding parsers for other data formats, technology partners, and atom probers.
If you would like to implement a parser for your data, feel free to get in contact.

## Development install

Install the package with its dependencies:

```shell
git clone https://github.com/FAIRmat-NFDI/pynxtools-apm.git --branch main --recursive pynxtools_apm
cd pynxtools_apm
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install -e ".[dev]"
```

There is also a [pre-commit hook](https://pre-commit.com/#intro) available
which formats the code and checks the linting before actually commiting.
It can be installed with
```shell
pre-commit install
```
from the root of this repository.

## Development Notes
TODO: Give details about envisioned development of the parser.

## Test this software

Especially relevant for developers, there exists a basic test framework written in
[pytest](https://docs.pytest.org/en/stable/) which can be used as follows:

```shell
python -m pytest -sv tests
```

## Contact person in FAIRmat for this reader
Markus Kühbach
