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
"""Generic parser for loading atom probe microscopy data into NXapm."""

from time import perf_counter_ns
from typing import Tuple, Any
import numpy as np

from pynxtools.dataconverter.readers.base.reader import BaseReader
from pynxtools_apm.utils.io_case_logic import (
    ApmUseCaseSelector,
)
from pynxtools_apm.utils.oasis_config_reader import (
    NxApmNomadOasisConfigurationParser,
)
from pynxtools_apm.utils.oasis_eln_reader import (
    NxApmNomadOasisElnSchemaParser,
)
from pynxtools_apm.utils.load_reconstruction import (
    ApmReconstructionParser,
)
from pynxtools_apm.utils.load_ranging import (
    ApmRangingDefinitionsParser,
)
from pynxtools_apm.utils.create_nx_default_plots import (
    apm_default_plot_generator,
)
# from pynxtools_apm.utils.apm_generate_synthetic_data import (
#     ApmCreateExampleData,
# )

# this apm parser combines multiple sub-parsers
# so we need the following input:
# > logical analysis which use case
# > data input from an ELN (currently NOMAD Oasis, eLabFTW, openBIS in the future)
# > data input from technology partner files
# > functionalities for creating default plots
# > developer functionalities for creating synthetic data

# for development purposes synthetic datasets can be created which that are for now stored
# all in the same file. As these use the same dictionary, the template variable analyses
# of files which are larger than the physical main memory is currently not supported


class APMReader(BaseReader):
    """Parse content from community file formats.

    Specifically, (local electrode) atom probe microscopy and field-ion microscopy
    into a NXapm.nxdl-compliant NeXus file.

    """

    # Whitelist for the NXDLs that the reader supports and can process
    supported_nxdls = ["NXapm"]

    def read(
        self,
        template: dict = None,
        file_paths: Tuple[str] = None,
        objects: Tuple[Any] = None,
    ) -> dict:
        """Read data from given file, return filled template dictionary apm."""
        tic = perf_counter_ns()
        template.clear()

        entry_id = 1
        if len(file_paths) == 1:
            pass
            """
            # TODO::better make this an option rather than hijack and demand a
            # specifically named file to trigger the synthesizer
            # the synthesize functionality is currently deactivated, we have enough
            # example datasets and the synthesizer is in need for a refactoring.
            if file_paths[0].startswith("synthesize"):
                synthesis_id = int(file_paths[0].replace("synthesize", ""))
                print(f"synthesis_id {synthesis_id}")
            else:
                synthesis_id = 1
            print("Create one synthetic entry in one NeXus file...")
            synthetic = ApmCreateExampleData(synthesis_id)
            synthetic.synthesize(template)
            """
        else:  # eln_data, and ideally recon and ranging definitions from technology partner file
            print("Parse ELN and technology partner file(s)...")
            case = ApmUseCaseSelector(file_paths)
            if not case.is_valid:
                print("Such a combination of input-file(s, if any) is not supported !")
                return {}
            case.report_workflow(template, entry_id)

            if len(case.cfg) == 1:
                print("Parse (meta)data coming from a configuration of an RDM...")
                nx_apm_cfg = NxApmNomadOasisConfigurationParser(
                    case.cfg[0], entry_id, False
                )
                nx_apm_cfg.parse(template)
            else:
                print("No input file defined for config data !")

            if len(case.eln) == 1:
                print("Parse (meta)data coming from an ELN...")
                nx_apm_eln = NxApmNomadOasisElnSchemaParser(case.eln[0], entry_id)
                nx_apm_eln.parse(template)
            else:
                print("No input file defined for eln data !")

            if len(case.reconstruction) == 1:
                print("Parse (meta)data from a reconstructed dataset file...")
                nx_apm_recon = ApmReconstructionParser(case.reconstruction[0], entry_id)
                nx_apm_recon.report(template)
            else:
                print("No input-file defined for reconstructed dataset!")

            if len(case.ranging) == 1:
                print("Parse (meta)data from a ranging definitions file...")
                nx_apm_range = ApmRangingDefinitionsParser(case.ranging[0], entry_id)
                nx_apm_range.report(template)
            else:
                print("No input-file defined for ranging definitions!")

        print("Create NeXus default plottable data...")
        apm_default_plot_generator(template, entry_id)

        # in the future we expect that there are sequential dependencies that may demand
        # conditional post-processing of the template or changing the order in which
        # sources of information are processed
        # e.g. if the user does not provide reconstruction and ranging definition
        # it is currently still possible to use NXapm because none of these are required
        # entries but if recon and ranging are absent it makes no sense to store
        # the config of the reconstruction as it provokes that incorrect or dummy
        # information is provided.
        # Therefore, currently empty strings from config or eln_data.yaml files are
        # considered non-filled in template instance data and are thus not copied over

        # print("Reporting state of template before passing to HDF5 writing...")
        # for keyword in template.keys():
        #     print(f"keyword: {keyword}, template[keyword]: {template[keyword]}")
        # exit(1)

        print("Forward instantiated template to the NXS writer...")
        toc = perf_counter_ns()
        trg = f"/entry{entry_id}/profiling"
        template[f"{trg}/@NX_class"] = "NXcs_profiling"
        template[f"{trg}/template_filling_elapsed_time"] = np.float64(
            (toc - tic) / 1.0e9
        )
        template[f"{trg}/template_filling_elapsed_time/@units"] = "s"
        return template


# This has to be set to allow the convert script to use this reader.
READER = APMReader
