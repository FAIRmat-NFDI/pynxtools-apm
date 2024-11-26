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
"""Entry points for XPS examples."""

try:
    from nomad.config.models.plugins import ExampleUploadEntryPoint
except ImportError as exc:
    raise ImportError(
        "Could not import nomad package. Please install the package 'nomad-lab'."
    ) from exc

apm_example = ExampleUploadEntryPoint(
    title="Atom Probe Microscopy",
    category="FAIRmat examples",
    description="""
        This example presents the capabilities of the NOMAD platform to store and standardize atom probe data.
        It shows the generation of a NeXus file according to the
        [NXapm](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXapm.html#nxapm)
        application definition and a successive analysis of an example data set.
        The example contains a small atom probe dataset from an experiment with a LEAP instrument to get you started
        and keep the size of your NOMAD installation small. Once started, we recommend changing the respective
        input file in the NOMAD Oasis ELN to run the example with your own datasets.
    """,
    resources=['nomad/examples/*']
)
