import machine
import utime
import network
import socket
import secrets
import urequests as requests
import hashlib, binascii

wdt = machine.WDT(timeout=8000)

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

led.on()

print("getting task file.")
wdt.feed()
r = requests.get(TASK_URL, timeout=5)
print("getting checksum")
wdt.feed()
r2 = requests.get(CHECKSUM_URL, timeout=5)
wdt.feed()
print("verifying checkum")
remote_sha1 = binascii.hexlify(hashlib.sha1(r.text).digest()).decode('ascii')
remote_check = r2.text.split()[0].strip()
wdt.feed()

local_sha1 = 'nomatch'
try:
    with open(TASK_FILE,'r') as f:
        contents = f.read()
        local_sha1 = binascii.hexlify(hashlib.sha1(contents).digest()).decode('ascii')
except Exception as e:
    print("failed to read task file")
        
print(remote_check)
print(remote_sha1)
print(local_sha1)
if (remote_check == remote_sha1 and remote_check != local_sha1):
    print ("writing file!")
    f = open(TASK_FILE,'w')
    f.write(r.text)
    f.close()
    
try:
    import task
except Exception as e:
    print("task failed to run: %s" % (e,))

while True:
    print("update?")

    r2 = requests.get(CHECKSUM_URL, timeout=5)
    remote_check = r2.text.split()[0].strip()
    if (remote_check != local_sha1):
        print("update!")
        machine.reset()

    for i in range(59):
        print("time is ticking")
        if wlan.isconnected():
            wdt.feed()
        utime.sleep(1)

