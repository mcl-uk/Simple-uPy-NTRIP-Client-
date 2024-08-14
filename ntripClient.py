
import socket, sys, time, os
import machine
from machine import Pin, UART
from ubinascii import b2a_base64 as b64encode

# ------------------------ Operating paramteres --------------------

ntripCaster   = "rtk2go.com"
userNamePwd   = "rtk2go@fishbeetle.co.uk:none" # no pwd rqd for rtk2go clients
mountPoint    = "JoeSeelsGPS"
userAgent     = "Dumb uPyNTRIP Client/0.1"
myLat, myLon  = 53, -1
myAlt         = 252
serialBaud    = 115200
txPin, rxPin  = 33, 9  # default pins for uart1 are 10,9 but see notes above

ntripPort     = 2101
ntripHost     = False  # not tested
ntripV2       = False  # not tested

# --------------------- globals/objects ------------------------------

byteCounter   = 0
casterAddress = ('0.0.0.0', ntripPort) # placeholder
uNamePwdB64   = b64encode(bytes(userNamePwd,'utf-8')).decode().strip()

ntripUART     = UART(1, baudrate=serialBaud, tx=txPin, rx=rxPin)
ntripSkt      = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# ----------------------------- support functions ----------------------------

def makeGGABytes():
    hour,minute,second = time.gmtime()[3:6]
    # sanitise lat/lon
    NS = "N"
    EW = "E"
    lon = myLon
    lat = myLat
    if lon > 180:
        lon -= 360
        lon *= -1
        EW = "W"
    elif (lon < 0) and (lon >= -180):
        lon *= -1
        EW = "W"
    elif lon < -180:
        lon += 360
    if lat < 0:
        lat *= -1
        NS = "S"
    lonDeg = int(lon)
    latDeg = int(lat)
    lonMin = (lon - lonDeg)*60
    latMin = (lat - latDeg)*60
    # construct GGA sentence
    timStr = "{:02d}{:02d}{:02d}.00".format(hour, minute, second)
    latStr = "{:02d}{:011.8f},{:s}".format(latDeg, latMin, NS)
    lonStr = "{:02d}{:011.8f},{:s}".format(lonDeg, lonMin, EW)
    altStr = "{:5.3f}".format(myAlt)
    ggaStr = f"GPGGA,{timStr},{latStr},{lonStr},1,05,0.19,+00400,M,{altStr},M,,"
    # calc checksum
    cksm = 0
    for char in ggaStr: cksm ^= ord(char)
    cksStr = "{:02X}".format(cksm)
    return bytes(f"${ggaStr}*{cksStr}\r\n",'ascii')

# Try to connect to the caster, return 0 if connected else err code
def casterConnect():
    headerOK = False
    ntripSkt.settimeout(10)
    try:
        ntripSkt.connect(casterAddress)
    except KeyboardInterrupt:
        return -1
    except:
        return 1 # rte during connect attempt
    getRq = f"GET /{mountPoint} HTTP/1.1\r\n"
    getRq += f"User-Agent: {userAgent}\r\n"
    getRq += f"Authorization: Basic {uNamePwdB64}\r\n"
    if ntripHost or ntripV2: getRq += f"Host: {ntripCaster}:{ntripPort}\r\n"
    if ntripV2: getRq += "Ntrip-Version: Ntrip/2.0\r\n"
    print(getRq)
    try:
        ntripSkt.sendall(bytes(f"{getRq}\r\n",'ascii'))
    except:
        return 2 # rte sending get rq
    try:
        bRxHeaders = ntripSkt.recv(4096).split(b"\r\n")
    except OSError: # time-out
        return 7 # get rq timed-out
    except KeyboardInterrupt:
        return -1
    except:
        return 3 # rte during hdr rx
    for bLine in bRxHeaders:
        try:
            line = bLine.decode().strip()
        except:
            break
        if line == '': break
        print(line)
        if line.upper().startswith('SOURCETABLE'):
            return 4 # Mountpoint not found
        else:
            headerOK |= line.upper().endswith(" 200 OK")
    if not headerOK:
        return 5 # connection problem
    # Send GGA sentence
    gga = makeGGABytes()
    print(gga.decode())
    try:
        ntripSkt.sendall(gga)
    except:
        return 6 # rte sending GGA sentence
    return 0

# Call frequently to service data transfer
def txfrDataTask():
    global byteCounter
    ntripSkt.settimeout(0.01)
    try:
        bData = ntripSkt.recv(128)
    except OSError: # time-out
        return 0
    except KeyboardInterrupt:
        return -1
    except:
        return 10 # txfr skt problem
    if len(bData) == 0: return 0
    byteCounter += len(bData)
    if ntripUART.write(bData) == len(bData): return 0    # write bData to serial port
    return 11 # failed to write data

# ------------------------- main init -----------------------------

# &&& establish/check WiFi internet connection

err = 0
try:
    casterAddress = socket.getaddrinfo(ntripCaster, ntripPort)[0][-1]
except:
    print('IP address lookup for caster', ntripCaster, 'failed!')
    err = 9 # addr look-up failed

lastBCnt = 0
lastSec  = int(time.time())
tNow     = lastSec
#
try:
    assert err == 0
    err = casterConnect()
    print('---')

    while err == 0: # ------------------- main loop --------------------

        # &&& modulate LED to confirm main loop

        time.sleep(0.01) # at 115KB ~11ms is rqd to txfr 128 bytes (uart has 256B buffer)
        tNow = int(time.time())
        err = txfrDataTask()
        #
        # do other stuff here
        #

        # Once a second...
        if lastSec != tNow:
            lastSec = tNow
            # indicate progress: output bytes counted since last update
            if lastBCnt != byteCounter:
                print('@{:11d} {:10d} Bytes'.format(tNow, byteCounter - lastBCnt))
                lastBCnt = byteCounter

except KeyboardInterrupt:
    err = -1

if err > 0:
    print (f"Error #{err} connecting / transferring RTCM data")
    print (f"Resetting for re-try in 10s...")
    time.sleep(10)
    machine.reset()

if err < 0: print("\r\n^C user exit")
try: ntripSkt.close()
except: pass

