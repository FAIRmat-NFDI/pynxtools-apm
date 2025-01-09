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
    from nomad.config.models.plugins import (
        AppEntryPoint,
        ExampleUploadEntryPoint,
    )
    from nomad.config.models.ui import (
        App,
        Column,
        Menu,
        MenuItemHistogram,
        MenuItemPeriodicTable,
        MenuItemTerms,
        SearchQuantities,
    )
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
    plugin_package="pynxtools_apm",
    resources=["nomad/examples/*"],
)


schema = "pynxtools.nomad.schema.NeXus"

nexus_app = AppEntryPoint(
    name="ApmApp",
    description="Atom probe tomography app.",
    app=App(
        # Label of the App
        label="Apm",
        # Path used in the URL, must be unique
        path="apmapp",
        # Used to categorize apps in the explore menu
        category="Experiment",
        # Brief description used in the app menu
        description="A simple search app customized for NeXus data from the research field of atom probe tomography.",
        # Longer description that can also use markdown
        # readme="This is a simple App to support basic search for NeXus based Experiment Entries.",
        # If you want to use quantities from a custom schema, you need to load
        # the search quantities from it first here. Note that you can use a glob
        # syntax to load the entire package, or just a single schema from a
        # package.
        search_quantities=SearchQuantities(
            include=[f"*#{schema}"],
        ),
        # Controls which columns are shown in the results table
        columns=[
            Column(quantity="entry_id", selected=True),
            Column(quantity=f"entry_type", selected=True),
            Column(
                title="definition",
                quantity=f"data.*.ENTRY[*].definition__field#{schema}",
                selected=True,
            ),
            Column(
                title="start_time",
                quantity=f"data.*.ENTRY[*].start_time__field#{schema}",
                selected=True,
            ),
            Column(
                title="title",
                quantity=f"data.*.ENTRY[*].title__field#{schema}",
                selected=True,
            ),
        ],
        # Dictionary of search filters that are always enabled for queries made
        # within this app. This is especially important to narrow down the
        # results to the wanted subset. Any available search filter can be
        # targeted here. This example makes sure that only entries that use
        # MySchema are included.
        filters_locked={"section_defs.definition_qualified_name": [schema]},
        # Controls the menu shown on the left
        menu=Menu(
            title="Material",
            items=[
                Menu(
                    title="elements",
                    items=[
                        MenuItemPeriodicTable(
                            quantity="results.material.elements",
                        ),
                        MenuItemTerms(
                            quantity="results.material.chemical_formula_hill",
                            width=6,
                            options=0,
                        ),
                        MenuItemTerms(
                            quantity="results.material.chemical_formula_iupac",
                            width=6,
                            options=0,
                        ),
                        MenuItemHistogram(
                            x="results.material.n_elements",
                        ),
                    ],
                )
            ],
        ),
        # Controls the default dashboard shown in the search interface
        dashboard={
            "widgets": [
                {
                    "type": "histogram",
                    "show_input": False,
                    "autorange": True,
                    "nbins": 30,
                    "scale": "linear",
                    "quantity": f"data.Root.ENTRY.start_time__field#{schema}",
                    "title": "Start time",
                    "layout": {
                        "lg": {"minH": 3, "minW": 3, "h": 4, "w": 12, "y": 0, "x": 0}
                    },
                },
                {
                    "type": "terms",
                    "show_input": False,
                    "scale": "linear",
                    "quantity": f"entry_type",
                    "title": "Entry Type",
                    "layout": {
                        "lg": {"minH": 3, "minW": 3, "h": 8, "w": 4, "y": 0, "x": 12}
                    },
                },
                {
                    "type": "periodic_table",
                    "scale": "linear",
                    "quantity": f"results.material.elements",
                    "layout": {
                        "lg": {"minH": 3, "minW": 3, "h": 4, "w": 12, "y": 4, "x": 0}
                    },
                },
            ]
        },
    ),
)
