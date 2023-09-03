import machine
import utime
import time
import array
import network
import socket
import secrets

SERVER_NAME="launmon.ddns.net"

led = machine.Pin("LED", machine.Pin.OUT)

adc = machine.ADC(0)
N = 1000

x = array.array("i", (0 for _ in range(N)))
m = array.array("f", (0 for _ in range(N)))
ix = 0

win_sum = 0
average = 0
dif_sum = 0
variance = 0
std = 0

def get_ip(host, port=80):
    addr_info = socket.getaddrinfo(host, port)
    return addr_info[0][-1][0]

def newsample(t):
    global x, ix, average, win_sum, dif_sum, variance, N
    x[ix] = adc.read_u16()
    new = x[ix]
    oix = ix
    ix = ix + 1 if (ix < N - 1) else 0
    old = x[ix]
    win_sum += new - old
    average = win_sum / N

    m[oix] = abs(new - average)
    dif_sum += m[oix] - m[ix]
    variance = dif_sum / N


timer = machine.Timer(-1)
timer.init(period=1, mode=machine.Timer.PERIODIC, callback=newsample)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASS)

led.off()
print("hi")
while not wlan.isconnected() and wlan.status() >= 0:
    utime.sleep(1)
    print("...")
print("wifi connected.")

wdt = machine.WDT(timeout=5000)

try:
    ip = get_ip(SERVER_NAME)
    print(ip)
except IOError:
    print("DNS failed")
    machine.reset()
        

led.on()
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server = (ip,secrets.PORT)

starttime = time.time()
timer2 = machine.Timer()
timer2.init(
    period=1000,
    mode=machine.Timer.PERIODIC,
    callback=lambda t: sock.sendto("%s\n" % variance, server),
)

utime.sleep(2)
wdt = machine.WDT(timeout=2000)
while True:
    print(variance)
    print("time is ticking")

    utime.sleep(1)
    if wlan.isconnected():
        wdt.feed()
