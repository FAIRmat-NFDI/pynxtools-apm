# ATO

The pynxtools-apm parser and normalizer reads the following content and maps them on respective NeXus concepts that are defined in the NXapm application definition:

| ATO | NeXus/HDF5 |
| --------------- | --------------  |
| Reconstructed positions (x, y, z) | :heavy_check_mark: |
| Mass-to-charge-state-ratio values (m/q) | :heavy_check_mark: |

The ATO format has been used in different places and types of instruments and has
seen an evolution of different version. Documentation for these formats in the scientific
literature is incomplete and not fully consistent. The ifes_apt_tc_data_modeling library
reads v3 and v5 and applies a scaling to the reconstructed positions.

Users of this parsing functionality should inspect carefully whether the results of especially
reconstructed ion positions is within the correct order of magnitude. If this is not the case,
it can safely be considered a bug in which case we would appreciate if you can file a 
[bug/issue here](https://github.com/atomprobe-tc/ifes_apt_tc_data_modeling) so that we
can fix these remaining issues with this parser.
