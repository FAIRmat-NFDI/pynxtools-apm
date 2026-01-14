[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![](https://github.com/FAIRmat-NFDI/pynxtools-apm/actions/workflows/pytest.yml/badge.svg)
![](https://github.com/FAIRmat-NFDI/pynxtools-apm/actions/workflows/pylint.yml/badge.svg)
![](https://github.com/FAIRmat-NFDI/pynxtools-apm/actions/workflows/publish.yml/badge.svg)
![](https://img.shields.io/pypi/pyversions/pynxtools-apm)
![](https://img.shields.io/pypi/l/pynxtools-apm)
![](https://img.shields.io/pypi/v/pynxtools-apm)
![](https://coveralls.io/repos/github/FAIRmat-NFDI/pynxtools-apm/badge.svg?branch=main)
[![DOI](https://zenodo.org/badge/759916501.svg)](https://doi.org/10.5281/zenodo.14263076)

# `pynxtools-apm`: A `pynxtools` reader for APM data

This `pynxtools` plugin was generated with [`cookiecutter`](https://github.com/cookiecutter/cookiecutter) using the [`pynxtools-plugin-template`](https://github.com/FAIRmat-NFDI/`pynxtools-plugin-template) template.

## Installation
It is recommended to use python 3.12 with a dedicated virtual environment for this package.
Learn how to manage [python versions](https://github.com/pyenv/pyenv) and
[virtual environments](https://realpython.com/python-virtual-environments-a-primer/).

This package is a reader plugin for [`pynxtools`](https://github.com/FAIRmat-NFDI/pynxtools) and can be
installed together with `pynxtools`:

```shell
uv pip install pynxtools[apm]
```

for the latest released version.

## Purpose

This reader plugin for [`pynxtools`](https://github.com/FAIRmat-NFDI/pynxtools) is used to translate diverse file formats from the scientific community and technology partners
within the field of atom probe tomography and field-ion microscopy into a standardized representation using the
[NeXus](https://www.nexusformat.org/) application definition [NXapm](https://fairmat-nfdi.github.io/nexus_definitions/classes/applications/NXapm.html#nxapm).


## Docs

More information about this pynxtools plugin is available in the [documentation](https://fairmat-nfdi.github.io/pynxtools-apm/). You will find information about getting started, how-to guides, the supported file formats, how to get involved, and much more there.

## Contact person in FAIRmat for this reader

Markus Kühbach

## How to cite this work

Kühbach, M., Brockhauser, S., Gault, B., Raabe, D., Weber, H., Koch, C., Draxl, C. (2025). pynxtools-apm: A pynxtools reader plugin for atom probe tomography and related field-ion microscopy (APM) data. Zenodo. https://doi.org/10.5281/zenodo.14263076