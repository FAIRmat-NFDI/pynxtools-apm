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

import os

import numpy as np
from pynxtools.dataconverter import helpers
from pynxtools.dataconverter.template import Template
from pynxtools.dataconverter.writer import Writer
from pynxtools.definitions.dev_tools.utils.nxdl_utils import find_definition_file

from pynxtools_apm import NAIVE_GRID_DEFAULT_VOXEL_SIZE
from pynxtools_apm.utils.default_plot import create_default_plot_reconstruction


def test_utils_default_plot(tmp_path):
    """Generate reconstructed volume (cuboid shape), cut quarter cuboid sector out."""
    n_xyz = (8, 6, 22)
    d = NAIVE_GRID_DEFAULT_VOXEL_SIZE.magnitude
    o_xyz = tuple([(0.5 * n_xyz[i] * d) for i in range(0, 3)])

    xyz = []
    for z in np.arange(0, n_xyz[2]):
        zpos = (0.5 + z) * d
        # place z + 1 points in each bin, for simplicity points overlaying exactly
        for y in np.arange(0, n_xyz[1]):
            ypos = (0.5 + y) * d
            for x in np.arange(0, n_xyz[0]):
                xpos = (0.5 + x) * d
                # +x+y quarter cut out
                if xpos >= o_xyz[0]:
                    if ypos < o_xyz[1]:
                        xyz.extend([(xpos, ypos, zpos)] * (z + 1))
                else:
                    xyz.extend([(xpos, ypos, zpos)] * (z + 1))

    template = Template()
    trg = f"/ENTRY[entry1]/atom_probeID[atom_probe]/reconstruction/reconstructed_positions"
    template[trg] = {}
    template[trg]["compress"] = np.asarray(xyz, dtype=np.float32)
    del xyz

    template = create_default_plot_reconstruction(template, 1)
    here = os.getcwd()

    # not required to store these
    del template[trg]["compress"]
    del template[trg]

    # transfer and writing part of pynx convert without validation
    nxdl_f_path = find_definition_file("NXapm")
    assert nxdl_f_path is not None

    entry_names = template.get_all_entry_names()
    for entry_name in entry_names:
        helpers.write_nexus_def_to_entry(template, entry_name, "NXapm")

    try:
        writer = Writer(
            data=template,
            nxdl_f_path=nxdl_f_path,
            output_path=os.path.join(tmp_path, "test_utils_default_plot.nxs"),
            append=False,
        )
        writer.write()
    except Exception as execinfo:
        print(str(execinfo.value))
        assert False

    assert True
