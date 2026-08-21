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
"""
APM app backed by the generated Python metainfo (nexus_parser_v2).

The app targets the ``Apm`` application definition.
Design app targets for ``Apm_paraprobe*`` or ``Apm_compositionspace*`` similarly.

Search depth
------------
NOMAD registers dynamically mapped quantities only down to a fixed sub-section
depth for allow-listed NeXus AppDefs.
"""

from nomad.config.models.plugins import AppEntryPoint
from nomad.config.models.ui import (
    App,
    Column,
    Menu,
    MenuItemHistogram,
    MenuItemPeriodicTable,
    MenuItemTerms,
    MenuSizeEnum,
    SearchQuantities,
)

schema = "pynxtools.nomad.metainfo.applications.Apm"

# sub-sections that repeat, i.e. that the archive stores as a list. Only these
# take a JMESPath projection in a column; the rest must not, or the cell
# resolves to null. Listed here rather than read from the section definitions,
# because importing the schema package from an app module is circular: the
# plugin machinery loads app entry points while the schema is still
# initializing. `test_as_column_matches_metainfo_repeats` asserts that this
# stays in sync with the generated metainfo.
REPEATING_SUB_SECTIONS = frozenset(
    {
        "ionID",
        "citeID",
        "userID",
        "eventID",
    }
)


def as_column(quantity: str) -> str:
    """Turn a filter quantity name into one usable as a results table column.

    Menu items aggregate over the search index and address a quantity by its
    plain name. Table cells instead extract a value from the returned archive
    data with JMESPath, which cannot step into a list implicitly. The projection
    must therefore match the schema exactly, in both directions::

        data.userID.name        -> null   (userID repeats, so it is a list)
        data.userID[*].name     -> ["..."]

    Some sub-sections repeat - ``citeID``, ``userID``, ``ionID``.
    A projection is inserted at every segment named in `REPEATING_SUB_SECTIONS`
    and nowhere else, at whatever depth it occurs.

    The projection is dropped again when the name is turned into an API request
    (``parseJMESPath`` in the GUI keeps only the field names), so filtering and
    sorting are unaffected. Names without a schema are returned unchanged.
    """
    path, separator, schema_suffix = quantity.partition("#")
    if not separator or not path.startswith("data."):
        return quantity

    segments = [
        f"{part}[*]" if part in REPEATING_SUB_SECTIONS else part
        for part in path.split(".")
    ]
    return f"{'.'.join(segments)}{separator}{schema_suffix}"


apm_app = AppEntryPoint(
    name="ApmApp",
    description="A Generic NOMAD App for Atom Probe Tomography.",
    app=App(
        # basic configuration
        label="APM",
        path="apm_app",
        category="Experiment",
        description="A search app customized for atom probe experiments.",
        search_quantities=SearchQuantities(
            include=[f"*#{schema}"],
        ),
        # controls which columns are shown in the results table
        columns=[
            Column(title="Entry ID", search_quantity="entry_type", selected=True),
            Column(
                title="Definition",
                search_quantity=f"data.definition#{schema}",
                selected=True,
            ),
            Column(title="File Name", search_quantity="mainfile", selected=True),
            Column(
                title="Start Time",
                search_quantity=f"data.start_time#{schema}",
                selected=True,
            ),
            Column(
                title="Description",
                search_quantity=f"data.description#{schema}",
                selected=True,
            ),
        ],
        # only entries to show
        filters_locked={"section_defs.definition_qualified_name": [schema]},
        # controls the menu on the left-hand side
        menu=Menu(
            title="Filters",
            size=MenuSizeEnum.SM,
            show_header=True,
            items=[
                Menu(
                    title="Elements",
                    size=MenuSizeEnum.XXL,
                    show_header=True,
                    items=[
                        MenuItemPeriodicTable(
                            search_quantity="results.material.elements",
                        ),
                        # MenuItemHistogram(
                        #     title="Number of Elements",
                        #     x="results.material.n_elements",
                        # ),
                    ],
                ),
                Menu(
                    title="Experiment",
                    show_header=True,
                    items=[
                        MenuItemTerms(
                            title="Definition",
                            search_quantity=f"data.definition#{schema}",
                        ),
                        MenuItemTerms(
                            title="Project Name",
                            search_quantity=f"data.project.name#{schema}",
                        ),
                    ],
                ),
                Menu(
                    title="Specimen",
                    show_header=True,
                    items=[
                        MenuItemTerms(
                            title="Name",
                            search_quantity=f"data.specimen.name#{schema}",
                        ),
                        # MenuItemTerms(
                        #     title="Experiment or Simulation",
                        #     search_quantity=f"data.specimen.is_simulation#{schema}",
                        # ),
                    ],
                ),
                Menu(
                    title="Acquisition",
                    show_header=True,
                    items=[
                        # TODO: NXapm make run_number an NX_CHAR
                        # MenuItemHistogram(
                        #     title="Run Number",
                        #     search_quantity=f"data.run_number#{schema}",
                        # ),
                        MenuItemHistogram(
                            title="Elapsed Time",
                            x=f"data.elapsed_time#{schema}",
                        ),
                        # MenuItemTerms(
                        #     title="Pulse Mode",
                        #     search_quantity=f"data.measurement.eventID.instrument.pulser.pulse_mode#{schema}",
                        # ),
                        # MenuItemTerms(
                        #     title="Local Electrode",
                        #     search_quantity=f"data.measurement.instrument.local_electrode.name#{schema}",
                        # ),
                        MenuItemTerms(
                            title="Instrument Type",
                            search_quantity=f"data.measurement.instrument.type#{schema}",
                        ),
                        # MenuItemTerms(
                        #     title="Instrument Serial Number",
                        #     search_quantity=f"data.measurement.instrument.fabrication.serial_number#{schema}",
                        # ),
                        MenuItemHistogram(
                            title="Total Event Golden",
                            x=f"data.atom_probeID[*].hit_finding.total_event_golden#{schema}",
                        ),
                        # MenuItemHistogram(
                        #     title="Total Event Incomplete",
                        #     x=f"data.atom_probeID[*].hit_finding.total_event_incomplete#{schema}",
                        # ),
                        # MenuItemHistogram(
                        #     title="Total Event Multiple",
                        #     x=f"data.atom_probeID[*].hit_finding.total_event_multiple#{schema}",
                        # ),
                        # MenuItemHistogram(
                        #     title="Total Event Partials",
                        #     x=f"data.atom_probeID[*].hit_finding.total_event_partials#{schema}",
                        # ),
                        # MenuItemHistogram(
                        #     title="Total Event Record",
                        #     x=f"data.atom_probeID[*].hit_finding.total_event_record#{schema}",
                        # ),
                    ],
                ),
                Menu(
                    title="Ranging",
                    show_header=True,
                    items=[
                        MenuItemTerms(
                            title="Ion Name",
                            search_quantity=f"data.atom_probeID[*].ranging.peak_identification.ionID[*].name#{schema}",
                        ),
                    ],
                ),
                Menu(
                    title="Reconstruction",
                    show_header=True,
                    items=[
                        MenuItemTerms(
                            title="Primary Element",
                            search_quantity=f"data.atom_probeID[*].reconstruction.config.primary_element#{schema}",
                        ),
                    ],
                ),
                Menu(
                    title="Authors",
                    show_header=True,
                    items=[
                        MenuItemTerms(
                            title="User Name",
                            search_quantity=f"data.userID[*].name#{schema}",
                        ),
                    ],
                ),
            ],
        ),
        # controls the free area on the right-hand side for interactive search widgets
        dashboard={
            "widgets": [
                {
                    "type": "periodic_table",
                    "scale": "linear",
                    "title": "Periodic Table",
                    "quantity": "results.material.elements",
                    "layout": {
                        "xxl": {
                            "minH": 3,
                            "minW": 3,
                            "h": 11,
                            "w": 16,
                            "y": 0,
                            "x": 16,
                        },
                        "xl": {"minH": 3, "minW": 3, "h": 4, "w": 12, "y": 4, "x": 0},
                        "lg": {"minH": 3, "minW": 3, "h": 8, "w": 18, "y": 0, "x": 0},
                        "md": {"minH": 3, "minW": 3, "h": 4, "w": 12, "y": 4, "x": 0},
                        "sm": {"minH": 3, "minW": 3, "h": 4, "w": 12, "y": 4, "x": 0},
                    },
                },
            ],
        },
    ),
)
