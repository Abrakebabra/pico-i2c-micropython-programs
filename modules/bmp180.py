import utime
import math

# Micropython

class BMP180:
    address = 0x77
    CONTROL_REG = 0xF4
    DATA_REG = 0xF6
    mode = 1 #0 ultra lower power, 1 standard, 2 high, 3 ultra high resolution
    i2c = None
    
    
    # Calibration data registers
    CAL_AC1_REG = 0xAA
    CAL_AC2_REG = 0xAC
    CAL_AC3_REG = 0xAE
    CAL_AC4_REG = 0xB0
    CAL_AC5_REG = 0xB2
    CAL_AC6_REG = 0xB4
    CAL_B1_REG = 0xB6
    CAL_B2_REG = 0xB8
    CAL_MB_REG = 0xBA
    CAL_MC_REG = 0xBC
    CAL_MD_REG = 0xBE

    # Calibration data variables
    calAC1 = 0
    calAC2 = 0
    calAC3 = 0
    calAC4 = 0
    calAC5 = 0
    calAC6 = 0
    calB1 = 0
    calB2 = 0
    calMB = 0
    calMC = 0
    calMD = 0

    def __init__(self, device):
        self.i2c = device
        self.read_calibration_data()
        
        

    def read_signed_16_bit(self, register):
        msbArray = bytearray(self.i2c.readfrom_mem(self.address, register, 1))
        lsbArray = bytearray(self.i2c.readfrom_mem(self.address, register + 0x01, 1))
        msb = msbArray[0]
        lsb = lsbArray[0]
        
        
        if msb > 127:
            msb -= 256
                
        return (msb << 8) + lsb

    def read_unsigned_16_bit(self, register):
        msbArray = bytearray(self.i2c.readfrom_mem(self.address, register, 1))
        lsbArray = bytearray(self.i2c.readfrom_mem(self.address, register + 0x01, 1))
        msb = msbArray[0]
        lsb = lsbArray[0]
        
        return (msb << 8) + lsb


    def read_calibration_data(self):
        self.calAC1 = self.read_signed_16_bit(self.CAL_AC1_REG)
        self.calAC2 = self.read_signed_16_bit(self.CAL_AC2_REG)
        self.calAC3 = self.read_signed_16_bit(self.CAL_AC3_REG)
        self.calAC4 = self.read_unsigned_16_bit(self.CAL_AC4_REG)
        self.calAC5 = self.read_unsigned_16_bit(self.CAL_AC5_REG)
        self.calAC6 = self.read_unsigned_16_bit(self.CAL_AC6_REG)
        self.calB1 = self.read_signed_16_bit(self.CAL_B1_REG)
        self.calB2 = self.read_signed_16_bit(self.CAL_B2_REG)
        self.calMB = self.read_signed_16_bit(self.CAL_MB_REG)
        self.calMC = self.read_signed_16_bit(self.CAL_MC_REG)
        self.calMD = self.read_signed_16_bit(self.CAL_MD_REG)
        
        
    def get_raw_temp(self):
        self.i2c.writeto_mem(self.address, self.CONTROL_REG, bytearray([0x2E]))
        
        utime.sleep(0.0045)
        
        raw_data = self.read_unsigned_16_bit(self.DATA_REG)
        return raw_data

    def temperatureCalc(self, rawTemperature):
        UT = rawTemperature

        X1 = 0
        X2 = 0
        B5 = 0
        actual_temp = 0.0

        X1 = ((UT - self.calAC6) * self.calAC5) / math.pow(2, 15)
        X2 = (self.calMC * math.pow(2, 11)) / (X1 + self.calMD)
        B5 = X1 + X2
        actual_temp = ((B5 + 8) / math.pow(2, 4)) / 10

        return actual_temp
        

    def temperature(self):
        UT = self.get_raw_temp()
        return self.temperatureCalc(UT)

    def get_raw_pressure(self):
        self.i2c.writeto_mem(self.address, self.CONTROL_REG, bytearray([0x34 + (self.mode << 6)]))

        utime.sleep(0.008)

        msbArray = bytearray(self.i2c.readfrom_mem(self.address, self.DATA_REG, 1))
        lsbArray = bytearray(self.i2c.readfrom_mem(self.address, self.DATA_REG + 1, 1))
        xlsbArray = bytearray(self.i2c.readfrom_mem(self.address, self.DATA_REG + 2, 1))
        msb = msbArray[0]
        lsb = lsbArray[0]
        xlsb = xlsbArray[0]

        raw_data = ((msb << 16) + (lsb << 8) + xlsb) >> (8 - self.mode)

        return raw_data

    def pressureCalc(self, rawTemperature, rawPressure):
        #Returns the actual pressure in hectopascal (1hPa = 100 Pa).
        UT = rawTemperature
        UP = rawPressure
        B3 = 0
        B4 = 0
        B5 = 0
        B6 = 0
        B7 = 0
        X1 = 0
        X2 = 0
        X3 = 0
        pressure = 0

        # These calculations are from the BMP180 datasheet, page 15

        # Not sure if these calculations should be here, maybe they could be
        # removed?
        X1 = ((UT - self.calAC6) * self.calAC5) / math.pow(2, 15)
        X2 = (self.calMC * math.pow(2, 11)) / (X1 + self.calMD)
        B5 = X1 + X2

        # Todo: change math.pow cals to constants
        B6 = B5 - 4000
        X1 = (self.calB2 * (B6 * B6 / math.pow(2, 12))) / math.pow(2, 11)
        X2 = self.calAC2 * B6 / math.pow(2, 11)
        X3 = X1 + X2
        B3 = (((self.calAC1 * 4 + int(X3)) << self.mode) + 2) / 4
        X1 = self.calAC3 * B6 / math.pow(2, 13)
        X2 = (self.calB1 * (B6 * B6 / math.pow(2, 12))) / math.pow(2, 16)
        X3 = ((X1 + X2) + 2) / math.pow(2, 2)
        B4 = self.calAC4 * (X3 + 32768) / math.pow(2,15)
        B7 = (UP - B3) * (50000 >> self.mode)

        if B7 < 0x80000000:
            pressure = (B7 * 2) / B4
        else:
            pressure = (B7 / B4) * 2

        X1 = (pressure / math.pow(2, 8)) * (pressure / math.pow(2, 8))
        X1 = (X1 * 3038) / math.pow(2, 16)
        X2 = (-7357 * pressure) / math.pow(2, 16)
        # Calculate and covert to hPa
        pressure = (pressure + (X1 + X2 + 3791) / math.pow(2, 4))/100
        return pressure


    def pressure(self):
        rawTemperature = self.get_raw_temp()
        rawPressure = self.get_raw_pressure()
        return self.pressureCalc(rawTemperature, rawPressure)


    def altitudeCalc(self, pressureArg, sea_level_pressure = 101325):
        # Calulates an estimated altitude, not very correct
        altitude = 0.0
        pressure = pressureArg

        altitude = 44330.0 * (1.0 - math.pow(pressure / sea_level_pressure, 0.00019029495))

        return altitude


    def altitude(self):
        pressure = float(self.pressure())
        return self.altitudeCalc(pressure)
        

    def tpa(self):
        rawTemp = self.get_raw_temp()
        rawPres = self.get_raw_pressure()
        t = self.temperatureCalc(rawTemp)
        p = self.pressureCalc(rawTemp, rawPres)
        a = self.altitudeCalc(p)
        
        return t, p, a


#bmp180 = BMP180(i2cDevice)
#temp = bmp180.temperature()
#print(f"Tmp: {round(temp, 2)}C")
#p = bmp180.pressure()
#print(f"Prs: {round(p)}hPa")
#alt = bmp180.altitude()
#print(f"Alt: {round(alt, 2)}m")
