import machine
import bh1750		# done 2022/09/04
import htu21d		# done 2022/09/04
import bmp180		# done 2022/09/06
import is31fl3731	# done 2022/09/18
import scd4x		# done 2022/09/18
import icp10125		# done 2022/09/19

import utime


class Controller:
    # initiates any device if plugged in, doesn't if not.
    # runs code if initiated, doesn't if not.
    # Lazy way to play around with different devices on
    # a breadboard or Pimoroni's breakout garden pack

    
    devices = []  # just addresses of stuff plugged in
    
    # Addresses
    bh1750Addr		= 0x23
    htu21dAddr 		= 0x40
    scd41Addr 		= 0x62
    icp10125Addr 	= 0x63
    is31fl3731Addr 	= 0x74
    bmp180Addr 		= 0x77
    
    # pico breakout garden pack is sdl=4 scl=5
    
    
    def __init__(self, sdaPin, sclPin):
        self.reinit(sdaPin, sclPin)
        
        
    
    def reinit(self, sdaPin, sclPin):
        # so everything can be re-initialised while running
        
        self.i2c = machine.I2C(0,
                          sda=machine.Pin(sdaPin),
                          scl=machine.Pin(sclPin),
                          freq=400000)        
    
        print(f"Scanning I2C bus SDA pin {sdaPin} and SCL pin {sclPin}...")
        self.devices = self.i2c.scan()

        if len(self.devices) == 0:
            print('No I2C devices found!')
        else:
            print('I2C devices found: ', len(self.devices))
            for device in self.devices:
                print("Decimal address: ", device, " | Hexa address: ", hex(device))
                
                if hex(device) == hex(self.bh1750Addr):
                    self.bh1750 = bh1750.BH1750(self.i2c)
                    print(f"BH1750 initiated on pins {sdaPin}(sda) and {sclPin}(scl)")
                elif hex(device) == hex(self.htu21dAddr):
                    self.htu21d = htu21d.HTU21D(self.i2c)
                    print(f"HTU21D initiated on pins {sdaPin}(sda) and {sclPin}(scl)")
                elif hex(device) == hex(self.bmp180Addr):
                    self.bmp180 = bmp180.BMP180(self.i2c)
                    print(f"BMP180 initiated on pins {sdaPin}(sda) and {sclPin}(scl)")
                elif hex(device) == hex(self.is31fl3731Addr):
                    self.is31fl3731 = is31fl3731.IS31FL3731(self.i2c)
                    print(f"IS31FL3731 initiated on pins {sdaPin}(sda) and {sclPin}(scl)")
                elif hex(device) == hex(self.scd41Addr):
                    self.scd41 = scd4x.SCD4X(self.i2c)
                    utime.sleep(0.05)
                    self.scd41.start_periodic_measurement()
                    print(f"SCD41 initiated on pins {sdaPin}(sda) and {sclPin}(scl)")
                elif hex(device) == hex(self.icp10125Addr):
                    self.icp10125 = icp10125.ICP10125(self.i2c)
                    print(f"ICP10125 initiated on pins {sdaPin}(sda) and {sclPin}(scl)")
        
    def halp(self):
        print("""
Functions:
BH1750 (lux)
    get_bh1750_l() returns lux
    format_bh1750_l(lux)
    get_and_print_bh1750()
  
HTU21D (humidity %, temperature C, dew point C)
    get_htu21d_htd() returns (h, t, d)
    format_htu21d_htd([h, t, d])
    get_and_print_htu21d()

BMP180 (temperature C, pressure hPa, altitude m)
    get_bmp180_tpa() returns (t, p, a)
    format_bmp180_tpa([t, p, a]) returns (t, p, a)
    get_and_print_bmp180()
    
IS31FL3731 (5x5 rgb pixel screen)
    set_pixel(self, x, y, r, g, b, brightness=1.0)
    set_multiple_pixels(self, indexes, from_colour, to_colour=None)  pixel index 0-24 (sweeping color from to if wanted)
    show()
    clear()
    
SCD41 (CO2 ppm, temperature C, humidity %)
    get_scd41_cth() returns (c, t, h)
    format_scd41_cth([c, t, h]) returns (tpa)
    get_and_print_scd41
    
ICP10125 (pressure hPa, altitude m, temperature C)
    get_icp10125_pat() returns (p, a, t)
    format_icp10125_pat([p, a, t])
    get_and_print_icp10125
  """)


    def check_object(self, object):
        # checks if device instance has been created
        if object != None:
            return True
        else:
            return False


    # BH1750
    def get_bh1750_l(self):
        if self.check_object(self.bh1750):
            try:
                return self.bh1750.lux()
            except:
                print("BH1750 disconnected since init")
                
                
    def format_bh1750_l(self, lux):
        return round(lux)
        

    def get_and_print_bh1750(self):
        if self.check_object(self.bh1750):
            try:
                lux = self.get_bh1750_l()
                luxFormatted = self.format_bh1750_l(lux)
                print(f"Lux: {luxFormatted} lux   (bh1750)")
            except:
                print("BH1750 error")


    # HTU21D
    def get_htu21d_htd(self):
        if self.check_object(self.htu21d):
            if self.htu21d != None:
                try:
                    return self.htu21d.htd()
                except:
                    print("HTU21D disconnected since init")
            
    def format_htu21d_htd(self, htd):
        return round(htd[0], 2), round(htd[1], 2), round(htd[2], 2)


    def get_and_print_htu21d(self):
        if self.check_object(self.htu21d):
            try:
                htd = self.get_htu21d_htd()
                
                htdFormatted = self.format_htu21d_htd(htd)
                print(f"Hum: {htdFormatted[0]}%   (htu21d)")
                print(f"Tem: {htdFormatted[1]}C   (htu21d)")
                print(f"Dew: {htdFormatted[2]}C   (htu21d)")
            except:
                print("HTU21D error")


    # BMP180
    def get_bmp180_tpa(self):
        if self.check_object(self.bmp180):
            try:
                return self.bmp180.tpa()
            except:
                print("BMP180 disconnected since init")
            
    def format_bmp180_tpa(self, tpa):
        return round(tpa[0], 2), round(tpa[1]), round(tpa[2], 2)
            
    
    def get_and_print_bmp180(self):
        if self.check_object(self.bmp180):
            try:
                tpa = self.get_bmp180_tpa()
                tpaFormatted = self.format_bmp180_tpa(tpa)
                print(f"Tmp: {tpaFormatted[0]}C   (bmp180)")
                print(f"Prs: {tpaFormatted[1]}hPa   (bmp180)")
                print(f"Alt: {tpaFormatted[2]}m   (bmp180)")
            except:
                print("BMP180 error")
    
    # IS31FL3731
    def rgb5x5_set_single(self, x, y, rgbArray, brightness):
        if self.check_object(self.is31fl3731):
            try:
                xHoriz = y	# flipping axis
                yVert = x	# flipping axis
                self.is31fl3731.set_pixel(xHoriz, yVert, rgbArray[0], rgbArray[1], rgbArray[2], brightness)
            except:
                print("IS31FL3731 error")
                
        
    def rgb5x5_set_multi(self, coordinates, colorArrayStart, colorArrayEnd=None):
        #coordinates as nested array such as [[0,1], [2,1], [1,5]]
        if self.check_object(self.is31fl3731):
            try:
                pixelIndex = []
                for pixel in coordinates:
                    x = pixel[0]
                    y = pixel[1]
                    index = x*4 + x*1 + y
                    pixelIndex.append(index)
                if len(pixelIndex) > 0:
                    self.is31fl3731.set_multiple_pixels(pixelIndex, colorArrayStart, colorArrayEnd)
                else:
                    print("no pixels in set_multiple_pixels")
            except:
                print("IS31FL3731 error")
        
            
    def rgb5x5_update(self):
        if self.check_object(self.is31fl3731):
            try:
                self.is31fl3731.show()
            except:
                print("IS31FL3731 error")
        
    def rgb5x5_clear(self):
        if self.check_object(self.is31fl3731):
            try:
                self.is31fl3731.clear()
            except:
                print("IS31FL3731 error")
        
    # SCD41
    def get_scd41_cth(self):
        if self.check_object(self.scd41):
            try:
                return self.scd41.measure()
            except:
                print("SCD41 disconnected since init")
        
    def format_scd41_cth(self, cth):
        return cth[0], round(cth[1], 2), round(cth[2], 2)
    
    def get_and_print_scd41(self):
        if self.check_object(self.scd41):
            try:
                cth = self.get_scd41_cth()
                
                cthFormatted = self.format_scd41_cth(cth)
                print(f"CO2: {cthFormatted[0]}ppm  (scd41)")
                print(f"Tem: {cthFormatted[1]}C    (scd41)")
                print(f"Hum: {cthFormatted[2]}%    (scd41)")
            except:
                print("SCD41 error")

    # ICP10125
    def get_icp10125_pat(self):
        if self.check_object(self.icp10125):
            try:
                return self.icp10125.measure()
            except:
                print("ICP10125 disconnected since init")
    
    def format_icp10125_pat(self, pat):
        return round(pat[0]), round(pat[1], 2), round(pat[2], 2)
    
    
    def get_and_print_icp10125(self):
        if self.check_object(self.icp10125):
            try:
                pat = self.get_icp10125_pat()
                
                patFormatted = self.format_icp10125_pat(pat)
                print(f"Prs: {patFormatted[0]} hPa  (icp10125)")
                print(f"Alt: {patFormatted[1]} m    (icp10125)")
                print(f"Tem: {patFormatted[2]} C    (icp10125)")
            except:
                print("ICP10125 error")


