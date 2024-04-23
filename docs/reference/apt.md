# APT

The pynxtools-apm parser and normalizer reads the following content and maps them on respective NeXus concepts that are defined in the NXapm application definition:

| APT | NeXus/HDF5 |
| --------------- | --------------  |
| Reconstructed positions (x, y, z) | :heavy_check_mark: |
| Mass-to-charge-state-ratio values (m/q) | :heavy_check_mark: |

The APT file format is a proprietary binary file format maintained by AMETEK/Cameca
that contains additional pieces of information. The ifes_apt_tc_data_modeling library>=0.2.1
can read all these information to the point what has been communicated by AMETEK/Cameca
to the public. The parser is currently not mapping it though on NeXus.
