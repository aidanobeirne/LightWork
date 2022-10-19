from enum import Enum


class jyUnits(Enum):
    jyuUndefined = 0
    jyuMillimeters = 1
    jyuMicrons = 2
    jyuNanometers = 3
    jyuAngstroms = 4
    jyuPicometers = 5
    jyuBandpass = 6
    jyuSteps = 7
    jyuWavenumbers = 8
    jyuDeltaWavenumbers = 9
    jyuElectronVolts = 10
    jyuNanoseconds = 11
    jyuMicroseconds = 12
    jyuMilliseconds = 13
    jyuSeconds = 14
    jyuMinutes = 15
    jyuHours = 16
    jyuVolts = 17
    jyuMillivolts = 18
    jyuMicrovolts = 19
    jyuAmperes = 20
    jyuMilliAmps = 21
    jyuMicroAmps = 22
    jyuCounts = 23
    jyuCountsPerSecond = 24
    jyuDegreesCelcius = 25
    jyuDegreesFahrenheit = 26
    jyuDegreesKelvin = 27
    jyuPixels = 28
    jyuTotalUnitsPlusOne = 29


class jyUnitsType(Enum):
    jyutWavelength = 0
    jyutSlitWidth = 1
    jyutTime = 2
    jyutTemperature = 3
    jyutDataUnits = 4
    jyutSpatial = 5
    jyutTotalTypesPlusOne = 6


class jyCCDDataType(Enum):
    JYMCD_ACQ_FORMAT_IMAGE = 0
    JYMCD_ACQ_FORMAT_SCAN = 1
