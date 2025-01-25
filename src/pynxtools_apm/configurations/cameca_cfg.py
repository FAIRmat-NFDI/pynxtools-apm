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
"""Dict mapping custom schema instances from eln_data.yaml file on concepts in NXapm."""

from pynxtools_apm.utils.pint_custom_unit_registry import ureg


"map": [("", "fComments"), ("", "fQuality"), ("", "fPrimaryElement")],
"map_to_f8": [
("", "fEfficiency"),
("", ureg.volt / ureg.nanometer ** 2, "fEvaporationField"),
("", ureg.millimeter, "fFlightPath"),
("", "??", "fImageCompression"),
("", "??", "fKfactor"),
("", ureg.nanometer ** 3, "fReconVolume"),
("", ureg.degrees, "fShankAngle"),
("", ureg.nanometer, "fTipRadius"),
("", ureg.nanometer, "fTipRadius0"),
("", ureg.volt, "fVoltage0"),
("", ureg.nanometer, "fXmax"),
("", ureg.nanometer, "fXmin"),
("", ureg.nanometer, "fYmax"),
("", ureg.nanometer, "fYmin"),
("", ureg.nanometer, "fZmax"),
("", ureg.nanometer, "fZmin")]

("", "fUserID")


("", "fAcqBuildVersion"),
("", "fAcqMajorVersion"),
("", "fAcqMinorVersion"),
("", "fCernRootVersion"),
("", "fImagoRootDate"),
("", "fImagoRootVersion"),
("", "fStreamVersion"),

("", "fSerialNumber"),

("", "fBcaSerialRev"),
("", "fFirmwareVersion"),
("", "fFlangeSerialNumber"),
("", "fHvpsType"),
("", "fLaserModelString"),
("", "fLaserSerialNumber"),
("", "fLcbSerialRev"),
("", "fMcpSerialNumber"),
("", "fPulserType"),
("", "fTaSerialRev"),
("", "fTdcType"),

("type", "fAcquisitionMode"),
("", "fApertureName"),
("", "fAtomProbeName"),
("", "fComments")
("", "fName"),
("", "fProjectName"),

("", "fLeapModel"),
("", "fLaserModel"),

("", ureg.torr, "fAnalysisPressure"),
("", ureg.volt, "fAnodeAccelVoltage")
("", ureg.second, "fElapsedTime"),
("", ureg.kilohertz, "fInitialPulserFreq"),
("", "fInstrumentComment"),
("", "fMaximumFlightPathMm"),
("", "fMcpEfficiency"),
("", "fMeshEfficiency"),
# fPidAlgorithmID
# fPidMaxInitialSlew
# fPidMaxTurnOnSlew
# fPidPropCoef
# fPidPulsesPerUpdate
# fPidTradHysterisis
# fPidTradStep
("", "fRawPathName"),
("", "fResults"),
("", "fRunNumber"),
("", "fSpecimenCondition"),
("", "fSpecimenName"),
("", "fSpecimenTemperature"),
("", "fStartISO8601"),
("", ureg.nanosecond, "fT0Estimate"),
# fTargetEvapRate
# fTargetPulseFraction
("", "fTotalEventGolden")
("", "fTotalEventIncomplete")
("", "fTotalEventMultiple")
("", "fTotalEventPartials")
("", "fTotalEventRecords")
