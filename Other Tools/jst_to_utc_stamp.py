import utime

class JSTStamp:
    # Because MicroPython isn't returning UTC on 2022-09-23
    # This class gets local JST and converts it back to UTC, then I can add the +09:00
    # outputs in format for TCX XML files like 2022-09-23T07:51:42+09:00
    
    utcTimeDiff = 32400 #seconds
    
    def lPadZero2(string):
        return "0" + string if len(string) < 2 else string

    def getTimeStamp(self):
        lt = utime.localtime()
        ltEpoch = utime.mktime(lt)
        utcEpoch = ltEpoch - self.utcTimeDiff
        utc = utime.gmtime(utcEpoch)
        YYYY = str(lt[0])
        MM = lPadZero2(str(utc[1]))
        DD = lPadZero2(str(utc[2]))
        hh = lPadZero2(str(utc[3]))
        mm = lPadZero2(str(utc[4]))
        ss = lPadZero2(str(utc[5]))

        return f"{YYYY}-{MM}-{DD}T{hh}:{mm}:{ss}+09:00"
