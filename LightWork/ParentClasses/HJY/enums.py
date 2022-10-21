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

class jyDeviceOperatingMode(Enum):
    jyDevOpModeNormal = 0
    jyDevOpModeAcqHWTimeBased = 1
    jyDevOpModeAcqSWTimeBased = 2
    jyDevOpModeAcqFKBurst = 3
    jyDevOpModeAcqFKBlast = 4
    jyDevOpModeAcqICCD = 5
    jyDevOpModeAcqAllowIntermediateRead = 6
    jyDevOpModeLAST = 7

class jyHardwareProperty(Enum):
    jyUndefined = 0
    jypMonoLinearDispersion = 1
    jypMonoBacklashAmount = 2
    jypMonoStepsPerUnit = 3
    jypMonoBaseUnits = 4
    jypMonoBaseGrating = 5
    jypMonoCurrentGrating = 6
    jypMonoMaxLimit = 7
    jypMonoMinLimit = 8
    jypMonoTiltAngle = 9
    jypMonoIncludedAngle = 10
    jypMonoFocalLength = 11
    jypMonoOrder = 12
    jypMonoCurrentWavelength = 13
    jypMonoMCDWavelengthDirection = 14
    jypBandpassUnits = 15
    jypSlitMaxLimit = 16
    jypSlitMinLimit = 17
    jypSlitBackLashAmount = 18
    jypSlitBaseUnits = 19 
    jypSlitStepsPerUnit = 20
    jypLaserLine = 21
    jypTotalHardwarePropertiesPlusOne = 22

class jyCommType(Enum):
    no_comm = 0
    jyGPIB = 1
    jySerial = 2
    jyIP = 3
    jyUSB = 4

class jyCommParamType(Enum):
    yCPTUndefined = 0
    jyCPTCommType = 1
    jyCPTPortNum = 2
    jyCPTDeviceName = 3
    jyCPTBaudRate = 4
    jyCPTDatabits = 5
    jyCPTParitybits = 6
    jyCPTStopbits = 7