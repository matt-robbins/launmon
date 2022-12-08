import machine
import utime
import array
import network
import socket

SSID = "goldjeep"
PASS = "beepbeep"
PORT = 5001
led = machine.Pin("LED", machine.Pin.OUT)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID,PASS)

print("hi")
while not wlan.isconnected() and wlan.status() >= 0:
    utime.sleep(1)
    print("...")
print("wifi connected.")

def get_ip(host, port=80):
    addr_info = socket.getaddrinfo(host, port)
    return addr_info[0][-1][0]

ip = get_ip("launmon.ddns.net")
print(ip)

led.on()
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server = (ip,PORT)

adc = machine.ADC(0)
N = 1000

x = array.array('i', (0 for _ in range(N)))

while True:
    sum = 0.0
    for s in range(0,N-1):
        x[s] = adc.read_u16()
        sum = sum + x[s]
        
    sum = sum / N
    norm = 0.0
    for s in range(0,N-1):
        norm = norm + abs(x[s]-sum)
        
    norm = norm/N
    sock.sendto("%s\n" % norm, server)
