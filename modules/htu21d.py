import math

# Micropython

class HTU21D:
    addr = 0x40
    haddr = 0xE5
    taddr = 0xE3
    resetaddr = 0xFE
    i2c = None
    
    
    def __init__(self, device):
        self.i2c = device
    
    def humidity(self):
        hData = self.i2c.readfrom_mem(self.addr, self.haddr, 3)
        sHum = (hData[0] * 256 + hData[1])
        return -6 + 125 * sHum / 65536
    
    def temperature(self):
        tData = self.i2c.readfrom_mem(self.addr, self.taddr, 3)
        sTemp = (tData[0] * 256 + tData[1])
        return -46.85 + 175.72 * sTemp / 65536        


    def dewCalc(self, humidity, temperature):
        aConst = 8.1332
        bConst = 1762.39
        cConst = 235.66
        
        partialPressure = 10 ** (aConst - bConst / (temperature + cConst))

        return - (bConst /
                    (math.log10(humidity * partialPressure / 100) - aConst)
                    + cConst)
        

    def dewpoint(self):
        h = self.humidity()
        t = self.temperature()
        return self.dewCalc(h, t)
        

    def htd(self):
        humidity = self.humidity()
        temperature = self.temperature()
        dewPoint = self.dewCalc(humidity, temperature)
        
        return humidity, temperature, dewPoint
