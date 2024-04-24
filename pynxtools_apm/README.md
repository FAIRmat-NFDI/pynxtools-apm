<!--# APM reader

## Getting started - usage related to NOMAD Oasis
This parser can be used to map numerical data and metadata inside frequently
used file formats of atom probe tomography and related field-ion microscopy
software tools into a NeXus HDF5 file which complies with a specific version
of the NXapm application definition.

If you are using a NOMAD Oasis, you can use this tool as follows.
1. Log-in to a NOMAD Oasis and navigate to the *Create Uploads* tab.
2. Select apm example from the list of available options.
3. Drag-and-drop the file with your reconstructed dataset via pos, epos, or apt,
   and add your ranging definitions file via rrng, or rng, or the fig files from
   Peter Felfer's Erlangen atom-probe-toolbox.
3. Edit the electronic lab notebook (ELN) schema inside the NOMAD Oasis and click the
   save button in the NOMAD Oasis GUI to save the data that you have entered into
   the ELN template. Clicking *save* will trigger the automatic generation
   of an eln_data.yaml file. Second, the clicking will trigger a run of the
   dataconverter/apm parser which generates a NXapm NeXus file based on the data
   in the reconstruction and ranging file and the eln_data.yaml file. Afterwards,
   the file will be displayed in the GUI and show up in the upload section of your Oasis.
   By default the converter performs a strong loss-less compression on the input
   as many of the stack data store integers with a low entropy. The compression may
   take some time. You can inspect the progress of the conversion in the console from
   which you started the NOMAD Oasis appworker.
4. If successful, a NeXus (nxs) file will appear in your upload. You can explore
   its content with the H5Web tools inside the NOMAD Oasis GUI and click interactively
   through the data including default plots. For atom probe these are a 3D discretized
   view of your reconstruction using 1nm rectangular binning and the mass spectrum
   with a default 0.01 Da binning an no additional corrections.
   If unsuccessful, the console from where you started the NOMAD appworker can help
   you with identifying if problems occurred.

## A request to take action by the technology partners
In fact, while the above-mentioned file formats and corresponding commercial software is routinely
used by numerous atom probers every day, the actual knowledge about the I/O routines has always
been on a few developers shoulders. In fact many of the open-source readers for file formats were
reverse-engineered. This is challenging because the amount of documentation that is available
for some file formats is neither exhaustive nor documented enough in detail.

This limits developers to decide and design how to best implement possible mappings of
specific binary numerical data and metadata into specifically named fields. We wish that
intensified exchange between technology partners like AMETEK/Cameca and the atom probe
community can help to improve the situation. Everybody is very welcomed to leave us
comments in the issue list (or drop us an email) to exchange specifically about this topic.-->
