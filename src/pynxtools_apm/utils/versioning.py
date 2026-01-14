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
"""Utility tool constants and versioning."""

from pynxtools_apm.utils._version import version as __version__

NX_APM_ADEF_NAME = "NXapm"
PYNX_APM_NAME = "pynxtools-apm/reader.py"


def get_apm_exec_version() -> str:
    # TODO:deprecate, remove when versions are properly resolved with the next NOMAD release
    # then also remove the function call altogether
    # tag = get_repo_last_commit()
    # if tag is not None:
    #     return f"https://github.com/FAIRmat-NFDI/pynxtools-em/commit/{tag}"
    if __version__ is not None:
        return f"{__version__}"
    else:
        return "UNKNOWN COMMIT"


PYNX_APM_VERSION = get_apm_exec_version()

# numerics
MASS_SPECTRUM_DEFAULT_BINNING = 0.01  # u
NAIVE_GRID_DEFAULT_VOXEL_SIZE = 1.0  # nm
