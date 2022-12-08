import machine
import utime
import array
import network
import socket

SSID = "goldjeep"
PASS = "beepbeep"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID,PASS)

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server = ("192.168.1.233",5000)

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
