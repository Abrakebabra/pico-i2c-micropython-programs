import machine
import utime
import _thread
import pa1010d
import icp10125
import random


onboardLED = machine.Pin("LED", machine.Pin.OUT)
i2c = machine.I2C(0,
              sda=machine.Pin(4),
              scl=machine.Pin(5),
              freq=400000)


lock = _thread.allocate_lock()
gps = pa1010d.PA1010D(i2c)
altimeter = icp10125.ICP10125(i2c)

lat = None
lon = None
alt = None
kph = None


activityName = str(random.randint(0, 10000)) + ".txt"

f = open(activityName, "w")
f.close()

def update():
    
    global gps
    global altimeter
    global lock
    
    global lat
    global lon
    global alt
    global kph
    
    
    f = open(activityName, "a")
    
    while True:
        
        t = utime.localtime()
        tEpoch = utime.mktime(t)
        
        lock.acquire()
        entry = f"{tEpoch},{lat},{lon},{kph},{alt}\n"
        lock.release()
        
        onboardLED.on()
        
        f.write(entry)
        f.flush()
        
        utime.sleep(0.1)
        onboardLED.off()
        utime.sleep(0.9)
        

def getData():
    global lat
    global lon
    global alt
    global kph
    global gps
    global altimeter
    global lock
    global run
    
    counter = 0

    while True:
        
        sentence = gps.read_sentence()
        try:
            result = gps.parse_sentence(sentence)
            
            if result != None:
                talkerID = result[0]
                source = result[1]
                if source == "GGA":
                    lock.acquire()
                    lat = result[2]
                    lon = result[3]
                    lock.release()

                elif source == "VTG":
                    lock.acquire()
                    kph = result[3]
                    lock.release()

        except:
            pass
        
        if counter == 0:
            try:
                pat = altimeter.measure()
                alt = round(pat[1], 1)
            except:
                pass
        
        counter += 1
        if counter > 4:
            counter = 0
        
        utime.sleep(0.1)
        


_thread.start_new_thread(getData, ())
update()

