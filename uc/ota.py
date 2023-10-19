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
        
def check_update():
    print("DNS")
    sockaddr = socket.getaddrinfo(SERVER_NAME, 7007)[0][-1]
    print("done.")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.7)

    try:
        sock.connect(sockaddr)
        cs = sock.recv(100).split()[0].strip().decode('ascii')
    except OSError as e:
        print("timed out waiting for checksum %s" % e)
        cs = 'ooo'
        
    sock.close()
    return cs

def update(remote_sha1):
    try:
        r = requests.get(TASK_URL, timeout=5)
    except OSError:
        print("timed out getting remote file")
    else:
        print("verifying checkum")
        dl_sha1 = binascii.hexlify(hashlib.sha1(r.text).digest()).decode('ascii')

        if (dl_sha1 == remote_sha1):
            print ("writing file!")
            with open(TASK_FILE,'w') as f:
                f.write(r.text)
        
test = machine.Pin(0, machine.Pin.IN,machine.Pin.PULL_UP)

print(test.value())
if test.value():
    wdt = machine.WDT(timeout=8000)
else:
    wdt = FakeWDT(8000)

SERVER_NAME="laundry.375lincoln.nyc"
TASK_URL="https://" + SERVER_NAME + "/ota-update/task.py"
TASK_FILE="task.py"
CHECKSUM_URL=TASK_URL + ".sha1sum"

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
        machine.reset()

print("wifi connected.")

led.off()

local_sha1 = 'xxx'
try:
    with open(TASK_FILE,'r') as f:
        local_sha1 = binascii.hexlify(hashlib.sha1(f.read()).digest()).decode('ascii')
except Exception as e:
    print("failed to read task file")
        
print("checking for update")
wdt.feed()
remote_sha1 = check_update()

led.on()

if (not remote_sha1 == local_sha1):
    print("getting task file.")
    wdt.feed()
    update(remote_sha1)
    
try:
    import task
except Exception as e:
    print("task failed to run: %s" % (e,))

while True:
    print("update?")
    remote_sha1 = check_update()
    if (not remote_sha1 in [local_sha1, 'ooo']):
        machine.reset()
    print("nope")
    for i in range(10):
        print("time is ticking")
        if wlan.isconnected():
            wdt.feed()
        utime.sleep(1)

