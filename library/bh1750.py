# Micropython

class BH1750:
    addr = 0x23
    memAddr = 0x10
    i2c = None
    
    def __init__(self, device):
        self.i2c = device
        
    def lux(self):
        data = self.i2c.readfrom_mem(self.addr, self.memAddr, 2)
        return (data[0] * 256 + data[1]) / 1.2
        

