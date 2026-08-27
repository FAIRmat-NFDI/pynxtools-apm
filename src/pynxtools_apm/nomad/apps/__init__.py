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

try:
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
except ImportError as exc:
    raise ImportError(
        "Could not import nomad package. Please install the package 'nomad-lab'."
    ) from exc

apm_schema = "pynxtools.nomad.metainfo.applications.Apm"

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
    description="A NOMAD App for Atom Probe Tomography.",
    app=App(
        # basic configuration
        label="APM",
        path="apm_app",
        category="Experiment",
        description="A search app customized for atom probe experiments.",
        search_quantities=SearchQuantities(
            include=[f"*#{apm_schema}"],
        ),
        # controls which columns are shown in the results table
        columns=[
            Column(title="Entry ID", search_quantity="entry_type", selected=True),
            Column(
                title="Definition",
                search_quantity=f"data.definition#{apm_schema}",
                selected=True,
            ),
            Column(title="File Name", search_quantity="mainfile", selected=True),
            Column(
                title="Start Time",
                search_quantity=f"data.start_time#{apm_schema}",
                selected=True,
            ),
            Column(
                title="Experiment Description",
                search_quantity=f"data.experiment_description#{apm_schema}",
                selected=True,
            ),
            Column(
                title="Description",
                search_quantity=f"data.description#{apm_schema}",
                selected=False,
            ),
        ],
        # only entries to show
        filters_locked={"section_defs.definition_qualified_name": [apm_schema]},
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
                            search_quantity=f"data.definition#{apm_schema}",
                        ),
                        MenuItemTerms(
                            title="Project Name",
                            search_quantity=f"data.project.name#{apm_schema}",
                        ),
                    ],
                ),
                Menu(
                    title="Specimen",
                    show_header=True,
                    items=[
                        MenuItemTerms(
                            title="Name",
                            search_quantity=f"data.specimen.name#{apm_schema}",
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
                        # TODO: note that currently https://gitlab.mpcdf.mpg.de/nomad-lab/nomad-FAIR/-/blob/develop/nomad/metainfo/elasticsearch_extension.py#L592
                        # restricts the traversal depth to at most four layers (3 + 1) e.g.
                        # "data.atom_probeID.hit_finding.total_event_golden" gets into the index
                        # "data.measurement.instrument.local_electrode.name#{schema}" gets not unless setting max_level = 4
                        # NOTE THOUGH THAT increasing max_level non-linearly increases memory consumption and slows down startup!
                        # TODO: NXapm make run_number an NX_CHAR
                        # MenuItemHistogram(
                        #     title="Run Number",
                        #     search_quantity=f"data.run_number#{schema}",
                        # ),
                        MenuItemHistogram(
                            title="Elapsed Time",
                            x=f"data.elapsed_time#{apm_schema}",
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
                            search_quantity=f"data.measurement.instrument.type#{apm_schema}",
                        ),
                        # MenuItemTerms(
                        #     title="Instrument Serial Number",
                        #     search_quantity=f"data.measurement.instrument.fabrication.serial_number#{schema}",
                        # ),
                        MenuItemHistogram(
                            title="Total Event Golden",
                            x=f"data.atom_probeID.hit_finding.total_event_golden#{apm_schema}",
                        ),
                        MenuItemHistogram(
                            title="Total Event Incomplete",
                            x=f"data.atom_probeID.hit_finding.total_event_incomplete#{apm_schema}",
                        ),
                        MenuItemHistogram(
                            title="Total Event Multiple",
                            x=f"data.atom_probeID.hit_finding.total_event_multiple#{apm_schema}",
                        ),
                        MenuItemHistogram(
                            title="Total Event Partials",
                            x=f"data.atom_probeID.hit_finding.total_event_partials#{apm_schema}",
                        ),
                        MenuItemHistogram(
                            title="Total Event Record",
                            x=f"data.atom_probeID.hit_finding.total_event_record#{apm_schema}",
                        ),
                    ],
                ),
                # Menu(
                #     title="Ranging",
                #     show_header=True,
                #     items=[
                #         MenuItemTerms(
                #             title="Ion Name",
                #             search_quantity=f"data.atom_probeID.ranging.peak_identification.ionID.name#{schema}",
                #         ),
                #     ],
                Menu(
                    title="Reconstruction",
                    show_header=True,
                    items=[
                        MenuItemHistogram(
                            title="Volume",
                            x=f"data.atom_probeID.reconstruction.volume#{apm_schema}",
                        ),
                        # MenuItemTerms(
                        #     title="Primary Element",
                        #     search_quantity=f"data.atom_probeID.reconstruction.config.primary_element#{schema}",
                        # ),
                        # MenuItemHistogram(
                        #     title="Image Compression",
                        #     x=f"data.atom_probeID.reconstruction.config.image_compression#{schema}",
                        # ),
                        # MenuItemHistogram(
                        #     title="Kfactor",
                        #     x=f"data.atom_probeID.reconstruction.config.kfactor#{schema}",
                        # ),
                        # MenuItemHistogram(
                        #     title="Efficiency",
                        #     x=f"data.atom_probeID.reconstruction.config.efficiency#{schema}",
                        # ),
                        # MenuItemHistogram(
                        #     title="Evaporation Field",
                        #     x=f"data.atom_probeID.reconstruction.config.evaporation_field#{schema}",
                        # ),
                        # MenuItemHistogram(
                        #     title="Flight Path",
                        #     x=f"data.atom_probeID.reconstruction.config.flight_path#{schema}",
                        # ),
                        # MenuItemHistogram(
                        #     title="Shank Angle",
                        #     x=f"data.atom_probeID.reconstruction.config.shank_angle#{schema}",
                        # ),
                        # MenuItemHistogram(
                        #     title="Tip Radius",
                        #     x=f"data.atom_probeID.reconstruction.config.tip_radius#{schema}",
                        # ),
                        # MenuItemHistogram(
                        #     title="Tip Radius Zero",
                        #     x=f"data.atom_probeID.reconstruction.config.tip_radius_zero#{schema}",
                        # ),
                        # MenuItemHistogram(
                        #     title="Voltage Zero",
                        #     x=f"data.atom_probeID.reconstruction.config.voltage_zero#{schema}",
                        # ),
                    ],
                ),
                Menu(
                    title="Authors",
                    show_header=True,
                    items=[
                        MenuItemTerms(
                            title="User Name",
                            search_quantity=f"data.userID.name#{apm_schema}",
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
                        "xxl": {"minH": 3, "minW": 3, "h": 8, "w": 12, "y": 0, "x": 0},
                        "xl": {"minH": 3, "minW": 3, "h": 8, "w": 12, "y": 0, "x": 0},
                        "lg": {"minH": 3, "minW": 3, "h": 8, "w": 12, "y": 0, "x": 0},
                        "md": {"minH": 3, "minW": 3, "h": 8, "w": 12, "y": 0, "x": 0},
                        "sm": {"minH": 3, "minW": 3, "h": 8, "w": 12, "y": 0, "x": 0},
                    },
                },
            ],
        },
    ),
)


prefix = "pynxtools.nomad.metainfo"
# schema = f"{prefix}.base_classes.Entry"
tool_cfg_schema = f"{prefix}.applications.ApmParaprobeToolConfig"
tool_res_schema = f"{prefix}.applications.ApmParaprobeToolResults"
ranger_cfg_schema = f"{prefix}.applications.ApmParaprobeRangerConfig"
ranger_res_schema = f"{prefix}.applications.ApmParaprobeRangerResults"
selector_cfg_schema = f"{prefix}.applications.ApmParaprobeSelectorConfig"
selector_res_schema = f"{prefix}.applications.ApmParaprobeSelectorResults"
surfacer_cfg_schema = f"{prefix}.applications.ApmParaprobeSurfacerConfig"
surfacer_res_schema = f"{prefix}.applications.ApmParaprobeSurfacerResults"
distancer_cfg_schema = f"{prefix}.applications.ApmParaprobeDistancerConfig"
distancer_res_schema = f"{prefix}.applications.ApmParaprobeDistancerResults"
tessellator_cfg_schema = f"{prefix}.applications.ApmParaprobeTessellatorConfig"
tessellator_res_schema = f"{prefix}.applications.ApmParaprobeTessellatorResults"
spatstat_cfg_schema = f"{prefix}.applications.ApmParaprobeSpatstatConfig"
spatstat_res_schema = f"{prefix}.applications.ApmParaprobeSpatstatResults"
nanochem_cfg_schema = f"{prefix}.applications.ApmParaprobeNanochemConfig"
nanochem_res_schema = f"{prefix}.applications.ApmParaprobeNanochemResults"
intersector_cfg_schema = f"{prefix}.applications.ApmParaprobeIntersectorConfig"
intersector_res_schema = f"{prefix}.applications.ApmParaprobeIntersectorResults"
clusterer_cfg_schema = f"{prefix}.applications.ApmParaprobeClustererConfig"
clusterer_res_schema = f"{prefix}.applications.ApmParaprobeClustererResults"


paraprobe_app = AppEntryPoint(
    name="ParaprobeToolboxApp",
    description="A NOMAD App for paraprobe-toolbox.",
    app=App(
        # basic configuration
        label="PARAPROBE",
        path="paraprobe_app",
        category="Experiment",
        description="A search app customized for paraprobe-toolbox.",
        search_quantities=SearchQuantities(
            include=[
                # f"*#{base_schema}",
                f"*#{tool_cfg_schema}",
                f"*#{tool_res_schema}",
                f"*#{ranger_cfg_schema}",
                f"*#{ranger_res_schema}",
                f"*#{selector_cfg_schema}",
                f"*#{selector_res_schema}",
                f"*#{surfacer_cfg_schema}",
                f"*#{surfacer_res_schema}",
                f"*#{distancer_cfg_schema}",
                f"*#{distancer_res_schema}",
                f"*#{tessellator_cfg_schema}",
                f"*#{tessellator_res_schema}",
                f"*#{spatstat_cfg_schema}",
                f"*#{spatstat_res_schema}",
                f"*#{nanochem_cfg_schema}",
                f"*#{nanochem_res_schema}",
                f"*#{intersector_cfg_schema}",
                f"*#{intersector_res_schema}",
                f"*#{clusterer_cfg_schema}",
                f"*#{clusterer_res_schema}",
            ],
        ),
        # controls which columns are shown in the results table
        columns=[
            Column(title="Entry ID", search_quantity="entry_type", selected=True),
            # Column(
            #     title="Definition",
            #     search_quantity=f"data.definition#{schema}",
            #     selected=True,
            # ),
            Column(title="File Name", search_quantity="mainfile", selected=True),
            # Column(
            #     title="Start Time",
            #     search_quantity=f"data.start_time#{_schema}",
            #     selected=True,
            # ),
            # Column(
            #     title="Experiment Description",
            #     search_quantity=f"data.experiment_description#{paraprobe_schema}",
            #     selected=True,
            # ),
            # Column(
            #     title="Description",
            #     search_quantity=f"data.description#{paraprobe_schema}",
            #     selected=False,
            # ),
        ],
        # only entries to show
        filters_locked={
            "section_defs.definition_qualified_name": [
                tool_cfg_schema,
                tool_res_schema,
                ranger_cfg_schema,
                ranger_res_schema,
                selector_cfg_schema,
                selector_res_schema,
                surfacer_cfg_schema,
                surfacer_res_schema,
                distancer_cfg_schema,
                distancer_res_schema,
                tessellator_cfg_schema,
                tessellator_res_schema,
                spatstat_cfg_schema,
                spatstat_res_schema,
                nanochem_cfg_schema,
                nanochem_res_schema,
                intersector_cfg_schema,
                intersector_res_schema,
            ]
        },
        # controls the menu on the left-hand side
        menu=Menu(
            title="Filters",
            size=MenuSizeEnum.SM,
            show_header=True,
            items=[
                Menu(
                    title="paraprobe-ranger config",
                    show_header=True,
                    items=[
                        MenuItemTerms(
                            title="Ranging Definitions Checksum",
                            search_quantity=f"data.rangeID.ranging.checksum#{ranger_cfg_schema}",
                        ),
                        MenuItemTerms(
                            title="Ranging Definitions File Name",
                            search_quantity=f"data.rangeID.ranging.file_name#{ranger_cfg_schema}",
                        ),
                    ],
                ),
                Menu(
                    title="paraprobe-ranger result",
                    show_header=True,
                    items=[
                        MenuItemHistogram(
                            title="Charge State",
                            x=f"data.iontypesID.ionID.charge_state#{ranger_res_schema}",
                        ),
                    ],
                ),
                Menu(
                    title="paraprobe-surfacer config",
                    show_header=True,
                    items=[
                        MenuItemTerms(
                            title="Preprocessing Method",
                            search_quantity=f"data.surface_meshingID.preprocessing.method#{surfacer_cfg_schema}",
                        ),
                        MenuItemHistogram(
                            title="Preprocessing Kernel Width",
                            x=f"data.surface_meshingID.preprocessing.kernel_width#{surfacer_cfg_schema}",
                        ),
                    ],
                ),
                Menu(
                    title="paraprobe-surfacer result",
                    show_header=True,
                    items=[
                        MenuItemTerms(
                            title="Type",
                            search_quantity=f"data.point_set_wrappingID.alpha_complexID.type#{surfacer_res_schema}",
                        ),
                        MenuItemHistogram(
                            title="Alpha",
                            x=f"data.point_set_wrappingID.alpha_complexID.alpha#{surfacer_res_schema}",
                        ),
                    ],
                ),
                Menu(
                    title="paraprobe-nanochem results",
                    show_header=True,
                    items=[
                        MenuItemTerms(
                            title="Delocalized and Normalized By",
                            search_quantity=f"data.delocalizationID.grid.normalization#{nanochem_res_schema}",
                        ),
                        # this does not work with tool_cfg_schema!
                        # MenuItemHistogram(
                        #     title="Iso-Surface Value",
                        #     x=f"data.delocalizationID.grid.iso_surfaceID.isovalue#{nanochem_res_schema}",
                        # ),
                    ],
                ),
            ],
        ),
        # controls the free area on the right-hand side for interactive search widgets
    ),
)
