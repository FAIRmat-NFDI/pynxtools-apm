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
"""Utilities for downloading datasets from the global atom probe community for testing purposes."""

import re

import requests


def download_requests(url: str) -> str:
    """Query url for dataset, identify the filename, download and return it or empty string."""
    query = requests.get(url, stream=True, allow_redirects=True)
    if query.status_code == 200:
        match = re.search(
            r'filename="?([^"]+)"?', query.headers.get("Content-Disposition", "")
        )
        if match:
            output_file_name = f"{match.group(1)}"
        else:  # fall-back
            output_file_name = url.rsplit("/", 1)[-1]
        with open(output_file_name, "wb") as fp:
            for chunk in query.iter_content(1024 * 1024):
                fp.write(chunk)
        return output_file_name
    return ""
