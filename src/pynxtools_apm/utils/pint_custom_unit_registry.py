#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""A customized unit registry for handling units with pint."""

import numpy as np
import pint
from pint import UnitRegistry

ureg = UnitRegistry()
# ureg.formatter.default_format = "D"
# https://pint.readthedocs.io/en/stable/user/formatting.html

# customizations for NeXus
ureg.define("nx_unitless = 1")
ureg.define("nx_dimensionless = 1")
ureg.define("nx_any = 1")

NX_UNITLESS = ureg.Quantity(1, ureg.nx_unitless)
NX_DIMENSIONLESS = ureg.Quantity(1, ureg.nx_dimensionless)
NX_ANY = ureg.Quantity(1, ureg.nx_any)


def is_not_special_unit(units: pint.Unit) -> bool:
    """True if not a special NeXus unit category."""
    for special_units in [NX_UNITLESS.units, NX_DIMENSIONLESS.units, NX_ANY.units]:
        if units == special_units:
            return False
    return True
