#!/bin/bash

# pseudo code to run a batch queue
dsrc="/"  # define where your test data are located, assure that files mentioned in eln_data.yaml and eventually in apm.oasis.specific.yaml are existent!

dataconverter convert apm.oasis.specific.yaml eln_data.yaml $dsrc/reconstruction.pos $dsrc/ranging.env --reader apm --nxdl NXapm --output=apm.nxs 1>stdout.apm.nxs.txt 2>stderr.apm.nxs.txt
