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
import sys
from multiprocessing import Process

import click
import pandas as pd
import yaml

from pynxtools_apm.examples.deu_berlin_kuehbach.batch import process_project
from pynxtools_apm.examples.deu_berlin_kuehbach.utils import (
    get_project_id,
    snake_case_to_camel_case,
)
from pynxtools_apm.utils.custom_logging import logger


def run(project_id: str) -> int:
    """Batch process all rows of project with project_id."""
    logger.info(os.getcwd())
    with open(f"{os.getcwd()}{os.sep}source_directory.txt") as fp:
        src_directory: str = f"{fp.readline().strip().replace('/', os.sep)}"
    logger.info(src_directory)
    with open(f"{os.getcwd()}{os.sep}target_directory.txt") as fp:
        trg_directory: str = f"{fp.readline().strip().replace('/', os.sep)}"
    logger.info(trg_directory)

    # os.makedirs(
    #     f"{trg_directory.replace('/decompressed', '/pynxtools')}", exist_ok=True
    # )
    # os.listdir(f"{trg_directory.replace('/decompressed', '')}")

    spread_sheet_of_all_projects = pd.read_excel(
        f"{src_directory}{os.sep}aaa_legacy_data.ods",
        sheet_name="aaa_legacy_data",
        engine="odf",
        dtype=str,
    ).fillna("")

    # with open(f"{src_directory}{os.sep}aaa_legacy_data.bib") as fp:
    #     bib = bibtexparser.load(fp).entries_dict

    with open(f"{src_directory}{os.sep}aaa_apm_nomad_project_names.yaml") as fp:
        nomad_project_names: dict[str, str] = yaml.safe_load(fp)

    project_range: tuple[int, int] = (1, 160)

    # TODO fix issues for project_id
    # 36, some assignments broken
    # 113 (too large allocations, likely unphysically large x, y, z coordinates)
    # 149 some assignments broken
    # bilal, (6, 6)
    # pauly, (73, 73)
    # uzuhashi (101, 101)

    count: int = 0
    for row in spread_sheet_of_all_projects.itertuples(index=True):
        # for local usage it is possible to process through all dataset
        # but publicly shared on NOMAD deployment requires filtering like this
        # if row.legal == "1" and row.use == "1":
        if (
            project_id == get_project_id(row.id)
            and project_range[0] <= int(project_id) <= project_range[1]
            and project_id in nomad_project_names
        ):

            def parse():
                # now each task call for all files of one NeXus file
                process_project(
                    project_id,
                    row.project_name,
                    f"{src_directory}{os.sep}{row.project_name}.ods",
                    f"{src_directory}{os.sep}aaa_legacy_data.bib",
                    f"{src_directory}{os.sep}{row.project_name}.sha256.results.csv",
                    trg_directory,
                    f"{trg_directory.replace('/decompressed', '/pynxtools')}",
                    openalex_file=f"{os.getcwd()}{os.sep}openalex/D_{snake_case_to_camel_case(row.project_name)}.json",
                    logger_file_path_suffix="paper.run01",
                    nomad_project_name=nomad_project_names[project_id],
                )

            p = Process(target=parse)
            p.start()
            p.join()

            count += 1

    logger.info(f"Batch queue completed {count}")
    return 0


@click.command()
@click.option(
    "--project",
    "project_id",
    required=True,
    type=str,
    help="001, 002, ... project_id",
)
def main(project_id: str) -> None:
    try:
        code = run(project_id)
        sys.exit(code)
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        sys.exit(130)
    except Exception:
        logger.exception("Unhandled exception")
        sys.exit(1)


if __name__ == "__main__":
    main()
