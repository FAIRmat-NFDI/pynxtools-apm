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
"""Utilities for working with NeXus concepts encoded as Python dicts in the concepts dir."""

from datetime import datetime
import pytz
import flatdict as fd
import numpy as np

from pynxtools_apm.utils.string_conversions import string_to_number
from pynxtools_apm.utils.interpret_boolean import try_interpret_as_boolean


def variadic_path_to_specific_path(path: str, instance_identifier: list):
    """Transforms a variadic path to an actual path with instances."""
    if (path is not None) and (path != ""):
        narguments = path.count("*")
        if narguments == 0:  # path is not variadic
            return path
        if len(instance_identifier) >= narguments:
            tmp = path.split("*")
            if len(tmp) == narguments + 1:
                nx_specific_path = ""
                for idx in range(0, narguments):
                    nx_specific_path += f"{tmp[idx]}{instance_identifier[idx]}"
                    idx += 1
                nx_specific_path += f"{tmp[-1]}"
                return nx_specific_path
    return None


def add_specific_metadata(
    concept_mapping: dict, orgmeta: fd.FlatDict, identifier: list, template: dict
) -> dict:
    """Map specific concept src on specific NeXus concept trg.

    concept_mapping: translation dict how trg and src are to be mapped
    orgmeta: instance data of src concepts
    identifier: list of identifier to resolve variadic paths
    template: instance data resulting from a resolved src to trg concept mapping
    """
    if "prefix_trg" in concept_mapping:
        variadic_prefix_trg = concept_mapping["prefix_trg"]
    elif "prefix" in concept_mapping:
        variadic_prefix_trg = concept_mapping["prefix"]
    else:
        raise KeyError(f"Neither prefix nor prefix_trg found in concept_mapping!")

    if "prefix_src" in concept_mapping:
        prefix_src = concept_mapping["prefix_src"]
    else:
        prefix_src = ""

    # process all mapping functors
    # (in graphical programming these are also referred to as filters or nodes), i.e.
    # an agent that gets some input does some (maybe abstract mapping) and returns an output
    # as the mapping can be abstract we call it functor
    if "use" in concept_mapping:
        for entry in concept_mapping["use"]:
            if isinstance(entry, tuple):
                trg = variadic_path_to_specific_path(
                    f"{variadic_prefix_trg}/{entry[0]}", identifier
                )
                template[f"{trg}"] = entry[1]
    if "map_to_str" in concept_mapping:
        for entry in concept_mapping["map_to_str"]:
            if isinstance(entry, tuple):
                if len(entry) == 1:
                    if isinstance(entry[0], str):
                        if f"{prefix_src}{entry[0]}" not in orgmeta:
                            continue
                        trg = variadic_path_to_specific_path(
                            f"{variadic_prefix_trg}/{entry[0]}", identifier
                        )
                        template[f"{trg}"] = orgmeta[f"{prefix_src}{entry[0]}"]
                elif len(entry) == 2:
                    if isinstance(entry[0], str) and isinstance(entry[1], str):
                        if f"{prefix_src}{entry[1]}" not in orgmeta:
                            continue
                        trg = variadic_path_to_specific_path(
                            f"{variadic_prefix_trg}/{entry[0]}", identifier
                        )
                        template[f"{trg}"] = orgmeta[f"{prefix_src}{entry[1]}"]
    if "map_to_bool" in concept_mapping:
        for entry in concept_mapping["map_to_bool"]:
            if isinstance(entry, tuple):
                if len(entry) == 1:
                    if isinstance(entry[0], str):
                        if f"{prefix_src}{entry[0]}" not in orgmeta:
                            continue
                        trg = variadic_path_to_specific_path(
                            f"{variadic_prefix_trg}/{entry[0]}", identifier
                        )
                        template[f"{trg}"] = try_interpret_as_boolean(
                            orgmeta[f"{prefix_src}{entry[0]}"])
                elif len(entry) == 2:
                    if isinstance(entry[0], str) and isinstance(entry[1], str):
                        if f"{prefix_src}{entry[1]}" not in orgmeta:
                            continue
                        trg = variadic_path_to_specific_path(
                            f"{variadic_prefix_trg}/{entry[0]}", identifier
                        )
                        template[f"{trg}"] = try_interpret_as_boolean(
                            orgmeta[f"{prefix_src}{entry[1]}"])
    if "map_to_real" in concept_mapping:
        for entry in concept_mapping["map_to_real"]:
            if isinstance(entry, tuple):
                if len(entry) == 1:
                    if isinstance(entry[0], str):
                        trg = variadic_path_to_specific_path(
                            f"{variadic_prefix_trg}/{entry[0]}", identifier
                        )
                        template[f"{trg}"] = string_to_number(
                            orgmeta[f"{prefix_src}{entry[0]}"]
                        )
                elif len(entry) == 2:
                    if isinstance(entry[1], str):
                        if f"{prefix_src}{entry[1]}" not in orgmeta:
                            continue
                        trg = variadic_path_to_specific_path(
                            f"{variadic_prefix_trg}/{entry[0]}", identifier
                        )
                        template[f"{trg}"] = string_to_number(
                            orgmeta[f"{prefix_src}{entry[1]}"]
                        )
                    elif isinstance(entry[1], list):
                        if not all(
                            (isinstance(value, str) and f"{prefix_src}{value}" in orgmeta)
                            for value in entry[1]
                        ):
                            continue
                        trg = variadic_path_to_specific_path(
                            f"{variadic_prefix_trg}/{entry[0]}", identifier
                        )
                        res = []
                        for value in entry[1]:
                            res.append(string_to_number(orgmeta[f"{prefix_src}{value}"]))
                        template[f"{trg}"] = np.asarray(res, np.float64)
    if "map_to_real_and_multiply" in concept_mapping:
        for entry in concept_mapping["map_to_real_and_multiply"]:
            if isinstance(entry, tuple) and len(entry) == 3:
                if isinstance(entry[1], str) and isinstance(entry[2], float):
                    if f"{prefix_src}{entry[1]}" not in orgmeta:
                        continue
                    trg = variadic_path_to_specific_path(
                        f"{variadic_prefix_trg}/{entry[0]}", identifier
                    )
                    template[f"{trg}"] = entry[2] * string_to_number(
                        orgmeta[f"{prefix_src}{entry[1]}"]
                    )
    if "map_to_real_and_join" in concept_mapping:
        for entry in concept_mapping["map_to_real_and_join"]:
            trg = variadic_path_to_specific_path(
                f"{variadic_prefix_trg}/{entry[0]}", identifier
            )
            if isinstance(entry[1], list):
                if not all(
                    (isinstance(value, str) and f"{prefix_src}{value}" in orgmeta)
                    for value in entry[1]
                ):
                    continue
                res = []
                for value in entry[1]:
                    res.append(string_to_number(orgmeta[f"{prefix_src}{value}"]))
                template[f"{trg}"] = np.asarray(res)
            # we may need to be more specific with the return datatype here
    if "unix_to_iso8601" in concept_mapping:
        for entry in concept_mapping["unix_to_iso8601"]:
            trg = variadic_path_to_specific_path(
                f"{variadic_prefix_trg}/{entry[0]}", identifier
            )
            if isinstance(entry[1], str):
                if f"{prefix_src}{entry[1]}" not in orgmeta:
                    continue
                template[f"{trg}"] = datetime.fromtimestamp(
                    int(orgmeta[f"{prefix_src}{entry[1]}"]), tz=pytz.timezone("UTC")
                ).isoformat()
                # TODO::is this really a UNIX timestamp
                # what about the timezone needs clarification from scientists !!!
    if "join_str" in concept_mapping:
        for entry in concept_mapping["join_str"]:
            trg = variadic_path_to_specific_path(
                f"{variadic_prefix_trg}/{entry[0]}", identifier
            )
            if isinstance(entry[1], list):
                if not all(
                    (isinstance(value, str) and f"{prefix_src}{value}" in orgmeta)
                    for value in entry[1]
                ):
                    continue
                res = []
                for value in entry[1]:
                    res.append(orgmeta[f"{prefix_src}{value}"])
                template[f"{trg}"] = " ".join(res)
    return template
