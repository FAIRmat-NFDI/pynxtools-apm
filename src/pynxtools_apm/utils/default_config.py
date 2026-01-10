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

"""Default parameters."""

from pynxtools_apm.utils.pint_custom_unit_registry import ureg

MASS_SPECTRUM_DEFAULT_BINNING = ureg.Quantity(0.01, ureg.dalton)
NAIVE_GRID_DEFAULT_VOXEL_SIZE = ureg.Quantity(1.0, ureg.nanometer)
DEFAULT_COMPRESSION_LEVEL = 9
