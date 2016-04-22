import StringIO
import base64
import colorsys
import math
import time
import sys
import PIL.Image
import PIL.ImageDraw
from websocketIO import *

wsio = None
img = None
draw = None

totalWidth = 0
totalHeight = 0
appId = ""
start = 0


def main():
    global wsio
    global img
    global draw
    global start

    wsio = websocketIO("ws://localhost:8086")
    wsio.on('initialize', initialize)
    wsio.on('setupDisplayConfiguration', setupDisplayConfiguration)
    wsio.on('requestNextFrame', requestNextFrame)

    img = PIL.Image.new("RGB", (1920, 1080), (60, 60, 60))
    draw = PIL.ImageDraw.Draw(img)
    start = time.time()

    render()

    wsio.open(on_open)  # starts in new thread, and waits indefinitely to listen


def render():
    global img
    global draw
    global start

    width, height = img.size
    center = [width / 2, height / 2]
    radius = 0.45 * min(width, height)

    now = time.time()

    hue, dummy = math.modf((now - start) / 10)

    r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 0.8)
    col = (int(255 * r), int(255 * g), int(255 * b))

    # draw in memory
    draw.ellipse((center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius), fill=col)


def captureFrame():
    global img

    # data = list(img.getdata())
    # pix = [x for t in data for x in t] # RGB buffer (as list)

    buf = StringIO.StringIO()
    img.save(buf, quality=80, format='JPEG')
    jpeg = buf.getvalue()
    buf.close()

    return base64.b64encode(jpeg)


def on_open():
    global wsio

    wsio.emit('addClient',
              {'clientType': "pythonApp", 'sendsMediaStreamFrames': True, 'receivesDisplayConfiguration': True});


def initialize(data):
    global wsio
    global appId
    global img

    appId = data['UID']

    width, height = img.size
    jpeg = captureFrame()

    wsio.emit('startNewMediaStream',
              {'id': appId + "|0", 'title': "Python App", 'src': jpeg, 'type': "image/jpeg", 'encoding': "base64",
               'width': width, 'height': height})
    print "started app"


def setupDisplayConfiguration(data):
    global totalWidth
    global totalHeight

    totalWidth = data['totalWidth']
    totalHeight = data['totalHeight']
    print "SAGE wall: " + str(totalWidth) + "x" + str(totalHeight)


def requestNextFrame(data):
    global appId

    render()
    jpeg = captureFrame()

    wsio.emit('updateMediaStreamFrame',
              {'id': appId + "|0", 'state': {'src': jpeg, 'type': "image/jpeg", 'encoding': "base64"}})


main()
