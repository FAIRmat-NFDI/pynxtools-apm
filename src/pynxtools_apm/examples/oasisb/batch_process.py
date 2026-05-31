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

"""Script to batch-convert to NeXus/HDF5 using pynxtools-apm."""

import io
import json
import logging
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import bibtexparser
import flatdict as fd
import pandas as pd
from ifes_apt_tc_data_modeling import get_ifes_apt_tc_data_modeling_version
from pynxtools.dataconverter.convert import convert
from pynxtools.dataconverter.helpers import (
    get_nxdl_root_and_path,
    get_pynxtools_version,
)

from pynxtools_apm import get_pynxtools_apm_version


class ISO8601Formatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(
            record.created,
            tz=ZoneInfo("Europe/Berlin"),
        )
        return dt.isoformat()


try:
    # pynxtools-camecaroot is not in the public domain!
    from pynxtools_camecaroot import get_pynxtools_camecaroot_version

    if get_pynxtools_camecaroot_version() != "unknown_version":
        USE_WORKING_CAMECAROOT_PLUGIN = True
    else:
        USE_WORKING_CAMECAROOT_PLUGIN = False
except (ImportError, ModuleNotFoundError):
    USE_WORKING_CAMECAROOT_PLUGIN = False

from pynxtools_apm.examples.oasisb.oasisb_eln import generate_oasis_specific_yaml
from pynxtools_apm.examples.oasisb.oasisb_utils import (
    APT_MIME_TYPES,
    CAMECA_ROOT_MIME_TYPES,
    CSV_HEADER_FOR_HASH_FILE,
)


def process_project(
    project_name: str,
    config_file: str,
    bib_file: str,
    hash_file: str,
    source_directory: str,
    target_directory: str,
    openalex_file: str = "",
    logger_file_path_suffix: str = "",
    # generate_eln_file: bool = True,
    # generate_nexus_file: bool = True,
    # time_zone_info: ZoneInfo = ZoneInfo("Europe/Berlin"),
) -> None:
    """Run first (if available) optional pynxtools-camecaroot followed by or only pynxtools-apm to generate a NeXus/HDF5 file for each dataset in the project named project_name.

    project_name : name of the legacy atom probe project for which this function processes all entries,
        e.g. "deu_duesseldorf_kuehbach" is a project-specific such name
    config_file : spreadsheet file (currently ods) that identifies which atom probe files (pos, rrng, ...)
        from the project should be combined into one entry in one NeXus/HDF5 file
    bib_file : bibtex bibliography file that resolves project-name-specific CitationKeys like
        D_DeuDuesseldorfKuehbach or A_DeuDuesseldorfKuehbach to populate NXcitation instances
    hash_file : csv file which stores the hash and original file name of each file from a project
    source_directory : location of atom probe files that the parser should convert
    target_directory : location where generated NeXus/HDF5 and log files should be stored
    openalex_file : (optional) project-name-specific JSON file, retrieved from OpenAlex
        to provide additional metadata context to a project, e.g. D_DeuDuesseldorfKuehbach.json
    logger_file_path_suffix : suffix to add to the name of the log file
    """

    config: dict[str, str] = {
        "python_version": f"{sys.version}",
        "working_directory": f"{os.getcwd()}",
        "project_name": project_name,
        "config_file": config_file,
        "bib_file": bib_file,
        "source_directory": source_directory,
        "target_directory": target_directory,
        "openalex_file": openalex_file,
        "pynxtools_version": f"{get_pynxtools_version()}",
        "ifes_apt_tc_data_modeling_version": f"{get_ifes_apt_tc_data_modeling_version()}",
        "pynxtools_apm_version": f"{get_pynxtools_apm_version()}",
    }
    if USE_WORKING_CAMECAROOT_PLUGIN:
        config["pynxtools_camecaroot_version"] = f"{get_pynxtools_camecaroot_version()}"
    else:
        config["pynxtools_camecaroot_version"] = "unknown_version or not_available"

    buffer = io.StringIO()
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(ISO8601Formatter(fmt="%(asctime)s;%(levelname)s;%(message)s"))
    logger = logging.getLogger(project_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    for key, original_path in config.items():
        print(f"INFO {key};{original_path}")

    nxdl = "NXapm"
    nxdl_root, nxdl_file = get_nxdl_root_and_path(nxdl)
    if not os.path.exists(nxdl_file):
        print(f"ERROR Unable to load {nxdl_file}")
        return

    try:
        spread_sheet_of_project = pd.read_excel(
            config_file,
            sheet_name=project_name,
            engine="odf",
            dtype=str,
        ).fillna("")
    except (FileNotFoundError, OSError):
        print(f"ERROR Unable to load {config_file}")
        return

    try:
        with open(bib_file) as fp:
            bib = bibtexparser.load(fp).entries_dict
    except (FileNotFoundError, OSError):
        print(f"ERROR Unable to load {bib_file}")
        return

    # compute hashes for each file when processing legacy data serves two purposes
    # assure as best as possible disjoint file names
    # enable to filter out duplicates
    # using hashes can be perceived though as cryptic if these appear
    # in the user interface of a research data management system
    # here we therefore wish to explore a mechanism of defining an alias for a file name
    # the files that get parsed follow the convention
    # f"{project_name}.{row_idx}.{col_idx}.{sha256sum}.{type.lower()}"
    # e.g.
    # "aus_sydney_bilal.0.3.2587bed623f3ec6399acadf3c92c8887e4977dfc220e66e8676f2f518a306eba.pos"
    # now we define a mapping which assigns this file again its original file name
    # "aus_sydney_bilal.zip:R18_60075-v01.pos"
    # the keys in file_to_hash end on the alias name
    # the values in file_to_hash end on the file with the hash, respectively
    try:
        with open(hash_file) as fp:
            start = next(
                idx for idx, line in enumerate(fp) if CSV_HEADER_FOR_HASH_FILE in line
            )
            df_hash = pd.read_csv(hash_file, sep=";", skiprows=start)
            df_hash.columns = ["path", "size", "mtime", "sha256"]

            # get the dictionary of hashes where to identify to replace original file names with short and clean unique ones
            file_to_hash: dict[str, str] = {}
            for line in df_hash.itertuples(index=True):
                for mime_type_list in [APT_MIME_TYPES, CAMECA_ROOT_MIME_TYPES]:
                    if line.path.lower().endswith(tuple(mime_type_list)):  # type: ignore
                        file_to_hash[line.path] = line.sha256  # type: ignore
    except (FileNotFoundError, OSError):
        print(f"ERROR Unable to load {hash_file}")
        return

    # we inject already queried content from the OpenAlex literature reference database
    # to inject additional metadata, this would also allow to add orcid provided the
    # original authors have individually added these upon publishing
    # given that this is often though not the case and given that combining
    # orcid and author name is legally an issue in Germany, we currently do not
    # autorecover the authors' orcid
    openalex = fd.FlatDict({}, delimiter="/")
    if openalex_file != "":
        try:
            with open(openalex_file, encoding="utf-8") as fp:
                openalex = fd.FlatDict(json.load(fp), delimiter="/")
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            print(f"ERROR Unable to load {openalex_file}")

    # one NeXus file per row, compositing from at least one atom probe file surplus
    # f"{project_name}.{row_idx}.oasis_specific.yaml ELN
    # this YAML ELN file is currently used for injecting citation references and the
    # file name aliasing, it can be used for injecting other metadata as well
    # metadata collected with different systems like APSuite, eLabFTW, or alike,
    # could also be injected here

    # we opted for a spreadsheet-based approach as this would also allow
    # to inject further metadata although we do not currently take advantage of it
    for row_idx in range(spread_sheet_of_project.shape[0]):
        has_input: bool = False
        for col_idx in range(1, 6):
            # resolves to one of these
            # camecaroot specific
            # 0, str_rraw, ignore
            # 1, rhit_hits
            # 2, root
            # open formats
            # 3, pos_epos_apt_ato_csv
            # 4, rng_rrng_fig_env
            # 5, hdf_xml_nxs_raw_ops
            # >= 6, ignore these columns
            original_path = spread_sheet_of_project.iat[row_idx, col_idx]  # type: ignore
            if original_path != "":
                has_input = True
                break
        if not has_input:
            print(f"WARNING No content to parse for row {row_idx}")
            continue

        # define the name of the NeXus file
        output_file_path = f"{target_directory}{os.sep}{project_name}.{row_idx}.nxs"
        if os.path.isfile(output_file_path):
            print(f"WARNING deleting older version of {output_file_path}")
            os.remove(output_file_path)
        print(f"INFO Compositing {output_file_path}")

        # file path aliasing
        alias_to_original: dict[str, str] = {}

        root_parser_used: bool = False
        if USE_WORKING_CAMECAROOT_PLUGIN:
            # if True, first run pynxtools-camecaroot generating the NeXus file
            # secondly, run pynxtools-apm appending if something to parse remains
            # if False, just run pynxtools-apm generating the NeXus file
            pynx_root_input_files: list[str] = []
            for col_idx in range(1, 3):  # ignore str_rraw and open formats
                original_path = spread_sheet_of_project.iat[row_idx, col_idx]  # type: ignore
                if original_path != "":
                    if original_path in file_to_hash:
                        alias_path = (
                            f"{source_directory}{os.sep}"
                            f"{project_name}.{row_idx}.{col_idx}."
                            f"{file_to_hash[original_path]}."  # type: ignore
                            f"{original_path.rsplit('.', 1)[1].lower()}"  # type: ignore
                        )
                        pynx_root_input_files.append(alias_path)
                        alias_to_original[alias_path] = original_path
                    else:
                        print(f"ERROR Unable to find hash for {row_idx}.{col_idx}")
                        pynx_root_input_files = []

            if len(pynx_root_input_files) > 0:
                print(f"INFO pynxtools-cameca")
                _ = convert(
                    input_file=tuple(pynx_root_input_files),
                    reader="camecaroot",
                    nxdl=nxdl,
                    append=False,
                    skip_verify=True,
                    ignore_undocumented=True,
                    output=output_file_path,
                )

        pynx_open_input_files: list[str] = []
        for col_idx in range(3, 6):  # only the open formats
            original_path = spread_sheet_of_project.iat[row_idx, col_idx]  # type: ignore
            if original_path != "":
                if original_path in file_to_hash:
                    alias_path = (
                        f"{source_directory}{os.sep}"
                        f"{project_name}.{row_idx}.{col_idx}."
                        f"{file_to_hash[original_path]}."  # type: ignore
                        f"{original_path.rsplit('.', 1)[-1].lower()}"  # type: ignore
                    )
                    pynx_open_input_files.append(alias_path)
                    alias_to_original[alias_path] = original_path
                    # note that original path does not resolve absolute but relative
                    # locations to not resolve secrets like on which computer the
                    # data were processed, e.g. if the file in practice is stored in
                    # /home/testuser/a.zip:b.pos original path will at least contain
                    # a.zip:b.pos but not necessarily a prefix
                else:
                    print(f"ERROR Unable to find hash for {row_idx}.{col_idx}")

        if not os.path.isfile(output_file_path):  # camecaroot did not ran or threw
            if len(pynx_open_input_files) == 0:
                logger.warning(
                    f"Not generating a NeXus file that would solely include ELN YAML metadata"
                )
                continue

        # okay, there is at least some content that we wish to parse for the row
        # collect all external metadata that is not stored in any atom probe specific file
        eln_file_path = generate_oasis_specific_yaml(
            target_directory,
            project_name,
            row_idx,  # type: ignore
            bib,  # type: ignore
            alias_to_original,
            write_yaml_file=True,
            # openalex,
        )
        if not os.path.isfile(eln_file_path):
            logger.error(
                f"Unable to generate {eln_file_path} whereby to get references to original authors' work"
            )
            continue

        pynx_open_input_files.append(eln_file_path)
        print(f"INFO pynxtools-apm {pynx_open_input_files}")
        # in every case ELN content has been added by pynxtools-apm
        if os.path.isfile(output_file_path):
            _ = convert(
                input_file=tuple(pynx_open_input_files),
                reader="apm",
                nxdl=nxdl,
                append=True,
                skip_verify=True,  # obsolete as append switches validation off anyway
                ignore_undocumented=True,
                output=output_file_path,
            )
        else:
            _ = convert(
                input_file=tuple(pynx_open_input_files),
                reader="apm",
                nxdl=nxdl,
                append=False,
                skip_verify=True,
                ignore_undocumented=True,
                output=output_file_path,
            )
        print(f"INFO {output_file_path} generated")

    with open(
        f"{target_directory}{os.sep}{project_name}.{logger_file_path_suffix}.csv", "w"
    ) as fp:
        fp.write(buffer.getvalue())

    print(f"Batch queue for project {project_name} processed successfully")
