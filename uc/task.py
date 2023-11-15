import machine
import time
import array
import socket
import secrets

SERVER_NAME="laundry.375lincoln.nyc"

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
count = 0
ip = "0.0.0.0"

def update_ip(host, port=80):
    global ip
    try:
        addr_info = socket.getaddrinfo(host, port)
        ip = addr_info[0][-1][0]
    except Exception as e:
        print("DNS failed: %s" % e)
        return

update_ip(SERVER_NAME)

def transmit(t):
#    update_ip(SERVER_NAME)
    server = (ip,secrets.PORT)
    sock.sendto("%0.2f\n" % variance, server)

def newsample(t):
    global count, x, ix, average, win_sum, dif_sum, variance, N
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
    if (count < 2*N):
        count += 1
        variance = 0


timer = machine.Timer(-1)
timer.init(period=1, mode=machine.Timer.PERIODIC, callback=newsample)

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

starttime = time.time()
timer2 = machine.Timer()
timer2.init(
    period=1000,
    mode=machine.Timer.PERIODIC,
    callback=transmit,
)

