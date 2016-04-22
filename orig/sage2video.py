__author__ = 'aaron.anderson'
import StringIO
import base64
import colorsys
import math
import time
import sys
import av
import PIL.Image
import PIL.ImageDraw

from websocketio import *
import VideoDecoder
import Queue


class SageVideo:
    def __init__(self):
        self.queue = Queue.Queue()
        #self.videodecoder = VideoDecoder.VideoDecoder(self.queue,'/home/sad/sage2/public/uploads/videos/May20thCondensedCoverage.mp4')
        #self.videodecoder.start()
        self.totalWidth = 0
        self.totalHeight = 0
        self.appId = ""
        #self.width = self.videodecoder.getWidth()
        #self.height =self.videodecoder.getHeight()
        self.video = av.open('/home/sad/Documents/SAGE2_Media/videos/May20thCondensedCoverage.mp4')
        self.width = self.video.streams[0].width
        self.height = self.video.streams[0].height

        self.wsio = WebSocketIO("ws://localhost")
        self.wsio.on('initialize',self.initialize)
        self.wsio.on('setupDisplayConfiguration', self.setupDisplayConfiguration)
        self.wsio.on('requestNextFrame', self.requestNextFrame)

        # self.captureFrame()
        self.wsio.open(self.on_open)


    def on_open(self):
        self.wsio.emit('addClient', {'clientType': "pythonApp",
                                'requests': {'config': True, 'version': False, 'time': False, 'console': False}})

        self.packets = self.video.demux()

    def setupDisplayConfiguration(self,data):
        self.totalWidth = data['totalWidth']
        self.totalHeight = data['totalHeight']
        print "SAGE wall: " + str(self.totalWidth) + "x" + str(self.totalHeight)

    def initialize(self,data):

        self.appId = data['UID']

        jpeg = self.makeInitialImage(self.width,self.height)

        self.wsio.emit('startNewMediaStream',
                  {'id': self.appId + "|0", 'title': "Python Video", 'src': jpeg, 'type': "image/jpeg", 'encoding': "base64",
                   'width': self.width, 'height': self.height})
        print "started app"

    def makeInitialImage(self,width,height):
        img = PIL.Image.new('RGB',(width,height),"white")
        buf = StringIO.StringIO()
        img.save(buf, quality=80, format='JPEG')
        jpeg = buf.getvalue()
        buf.close()
        return base64.b64encode(jpeg)

    def requestNextFrame(self,data):

        jpeg = self.captureFrame()

        self.wsio.emit('updateMediaStreamFrame',
                  {'id': self.appId + "|0", 'state': {'src': jpeg, 'type': "image/jpeg", 'encoding': "base64"}})


    def sendNextFrame(self,jpeg):
        self.wsio.emit('updateMediaStreamFrame',
                  {'id': self.appId + "|0", 'state': {'src': jpeg, 'type': "image/jpeg", 'encoding': "base64"}})

    def captureFrame(self):
        # try:
        #     jpeg = self.queue.get_nowait()
        #     self.queue.task_done()
        #     return jpeg
        # except:
        #     pass
        packet = self.packets.next()
        for frame in packet.decode():
            if packet.stream.type == 'video':
                img = frame.to_image()
                buf = StringIO.StringIO()
                img.save(buf, quality=80, format='JPEG')
                jpeg = buf.getvalue()
                buf.close()
                # self.sendNextFrame(base64.b64encode(jpeg))
                return jpeg
            else:
                print packet.stream.type
                self.captureFrame()







if __name__ == '__main__':
    video = SageVideo()
    print video