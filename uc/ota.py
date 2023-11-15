import machine
import utime
import network
import socket
import secrets
import urequests as requests
import hashlib, binascii

class FakeWDT:
    def __init__(self,timeout=5000):
        self.timeout = timeout
        self.timer = machine.Timer()
        self.feed()

    def feed(self):
        self.timer.init(
            period=self.timeout,
            mode=machine.Timer.ONE_SHOT,
            callback=lambda t: print("Fake WDT timed out!"),
        )

BASE_URL="http://laundry.375lincoln.nyc/ota-update/"
CHECKSUM_EXT=".sha1sum"

FILE_HASHES = {}

def check_update(file, wdt):
    url = BASE_URL+file
    cs_url = url+CHECKSUM_EXT
    local_cs = 'xxx'
    try:
        local_cs = FILE_HASHES[file]
    except KeyError:
        print("no hash in dict for %s" % file)
        try:
            with open(file,'r') as f:
                local_cs = binascii.hexlify(hashlib.sha1(f.read()).digest()).decode('ascii')
        except Exception as e:
            print("failed to read '%s'" % file)
        else:
            FILE_HASHES[file] = local_cs
    
    try:
        r = requests.get(cs_url, timeout=1)
        remote_cs = r.text.split()[0].strip()
    except OSError:
        print("timed out getting checksum")
        return False
    
    wdt.feed()
    if (remote_cs == local_cs):
        return False
    
    try:
        r = requests.get(url, timeout=1)
    except OSError:
        print("timed out getting remote file")
        return False
    
    wdt.feed()
    print("verifying checkum")
    dl_cs = binascii.hexlify(hashlib.sha1(r.text).digest()).decode('ascii')

    if (dl_cs != remote_cs):
        print("checksum failed")
        return False
    
    wdt.feed()
    print ("writing file!")
    try:
        with open(file,'w') as f:
            f.write(r.text)
    except Exception as e:
        print("failed to write file!")
        return False
        
    return True

test = machine.Pin(0, machine.Pin.IN,machine.Pin.PULL_UP)

if test.value():
    wdt = machine.WDT(timeout=8000)
else:
    wdt = FakeWDT(8000)
    
def reset():
    if test.value():
        machine.reset()
    else:
        print("resetting... PSych! You gotta do it.")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASS)

led = machine.Pin("LED", machine.Pin.OUT)

led.off()
print("hi")
count = 0
while not wlan.isconnected():
    utime.sleep(1)
    led.toggle()
    print("...")
    wdt.feed()
    count += 1
    if (count > 30):
        reset()

print("wifi connected.")

led.off()
if check_update("main.py",wdt):
    reset()
    
check_update("remote.py",wdt)
    
led.on()

try:
    import remote
except Exception as e:
    print("task failed to run: %s" % (e,))

while True:
    print("update?")
    if check_update("remote.py",wdt):
        reset()
    
    for i in range(10):
        if wlan.isconnected():
            wdt.feed()
        utime.sleep(1)
