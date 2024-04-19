# CSV

The pynxtools-apm parser and normalizer reads the following content and maps them on respective NeXus concepts that are defined in the NXapm application definition:

| CSV | NeXus/HDF5 |
| --------------- | --------------  |
| Reconstructed positions (x, y, z) | :heavy_check_mark: |
| Mass-to-charge-state-ratio values (m/q) | :heavy_check_mark: |

Occasionally, atom probers export portions of a reconstruction as comma-separated ASCII files.
We consider this to be an unnecessary inefficient and inaccurate approach that should be replaced
by self-descriptive formats like NeXus, POS, ePOS. In every case at least a header should be specified
which details the information that is stored in each column but examples from the literature show that
this is not always supplied.

The ifes_apt_tc_data_modeling library ==0.2.1 therefore makes strong assumptions when trying to
reading from CSV file:
- The format is comma-separated text
- Splitting on the separator results in a table with one row for each ion and four columns.
- The first three columns in sequence are mapped to reconstructed positions (x, y, z)
- The fourth column is mapped to mass-to-charge-state-ratio values

Users of this parsing functionality should inspect carefully whether the results are to their expectation.
If this is not the case, feel free to submit an issue [issue here](https://github.com/atomprobe-tc/ifes_apt_tc_data_modeling)
so that we can inspect and eventually fix this issue or guide how to use possible alternatives.
