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
"""Dict mapping values for a specifically configured NOMAD Oasis."""

# currently by virtue of design NOMAD Oasis specific examples show how different tools and
# services can be specifically coupled and implemented so that they work together
# currently we assume that the ELN provides all those pieces of information to instantiate
# a NeXus data artifact which technology-partner-specific files or database blobs can not
# deliver. Effectively a reader uses the eln_data.yaml generic ELN output to fill in these
# missing pieces of information while typically heavy data (tensors etc) are translated
# and written from the technology-partner files
# for large application definitions this can lead to a practical inconvenience:
# the ELN that has to be exposed to the user is complex and has many fields to fill in
# just to assure that all information are included in the ELN output and thus consumable
# by the dataconverter
# taking the perspective of a specific lab where a specific version of an ELN provided by
# or running in addition to NOMAD Oasis is used many pieces of information might not change
# or administrators do not wish to expose this via the end user ELN in an effort to reduce
# the complexity for end users and make entering of repetitiv information obsolete

# this is the scenario for which deployment_specific mapping shines
# parsing of deployment specific details in the apm reader is currently implemented
# such that it executes after reading generic ELN data (eventually available entries)
# in the template get overwritten

import datetime as dt

from pynxtools_apm.utils.versioning import NX_APM_ADEF_NAME


APM_OASISCONFIG_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]",
    "use": [
        ("definition", f"{NX_APM_ADEF_NAME}"),
        (
            "start_time",
            f"{dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')}",
        ),
    ],
    "map_to_str": [("operation_mode")],
}


APM_CSYS_MCSTASLIKE_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]/coordinate_system_set/COORDINATE_SYSTEM[coordinate_system]",
    "use": [
        (
            "alias",
            "Following the idea of McStas that the z-axis points along the direction of an ion leaving the apex along the longest direction of the specimen",
        ),
        ("type", "cartesian"),
        ("handedness", "right_handed"),
        (
            "x_direction",
            "Direction 1 that is perpendicular to the z_direction for a right_handed cartesian",
        ),
        ("x_alias", "x-axis"),
        (
            "y_direction",
            "Direction 2 that is perpendicular to the x_direction and the z_direction for a right_handed cartesian",
        ),
        ("y_alias", "y-axis"),
        (
            "z_direction",
            "Direction of an ion travelling hypothetically exactly along the assumed axis that is parallel to the longest direction of the specimen",
        ),
        ("z_alias", "z-axis"),
        (
            "origin",
            "E.g. a characteristic point e.g. initial apex or center of the base of the specimen or something else",
        ),
    ],
}


APM_EXAMPLE_TO_NEXUS = {
    "prefix_trg": "/ENTRY[entry*]/CITE[cite*]",
    "map_to_str": [("doi"), ("description")],
}
