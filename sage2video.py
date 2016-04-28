import cStringIO
import base64
import argparse
import av
import sys
import Queue

import time

from VideoDecoder import VideoDecoder
from threading import Thread

from websocketio import WebSocketIO
station_config = {'kfor':{'url':'http://localhost:8090/ch4',
                          'title':'KFOR Ch 4 (NBC)'},
                  'koco': {'url': 'http://localhost:8090/ch5',
                           'title': 'KOCO Ch 5 (ABC)'},
                'kwtv': {'url': 'http://localhost:8090/ch9',
                         'title': 'KWTV Ch 9 (CBS)'},
                'kokh': {'url': 'http://localhost:8090/ch12',
                         'title': 'KOKH Ch 12 (FOX)'}
                  }

class SageVideo(object):
    def __init__(self,station):
        super(SageVideo, self).__init__()
        self.station = station
        self.wsio = WebSocketIO("ws://localhost")
        self.queue = Queue.Queue(maxsize=1800)
        self.video = VideoDecoder(self.queue,station_config[self.station]['url'])
        self.video.setDaemon(True)
        self.wsio.open(self.on_open)

    def on_open(self):
        self.wsio.on('initialize', self.initialize)
        self.wsio.on('setupDisplayConfiguration', self.setupDisplayConfiguration)
        self.wsio.on('requestNextFrame', self.requestNextFrame)
        self.wsio.on('stopMediaCapture', self.stopMediaCapture)
        self.wsio.emit('addClient', {'clientType': "tvApp_{}".format(self.station),
                                'requests': {'config': True, 'version': False, 'time': False, 'console': False}})

    def initialize(self,data):
        print 'in initialize'
        self.appId = data['UID']+'|0'
        self.video.setAppId(self.appId)
        print 'appId is', self.appId
        self.video.start()
        print "started app"

    def requestNextFrame(self,data):
        nextframe = self.queue.get()
        self.wsio.emit('updateMediaBlockStreamFrame',nextframe)



    def setupDisplayConfiguration(self,data):
        self.width = self.video.getWidth()
        self.height = self.video.getHeight()
        self.wsio.emit('startNewMediaBlockStream',
                       {'id': self.appId, 'title': station_config[self.station]['title'], 'color':'#FFFFFF', 'colorspace': 'RGBA',
                        'width': self.width, 'height': self.height})

    def stopMediaCapture(self,data):
        print "Stop media capture and exit"
        self.video.running = False
        sys.exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Display TV on SAGE2 Display")
    parser.add_argument('station', type=str,help="Television station (kfor,kwtv,koco,kokh")
    args = parser.parse_args()
    test = SageVideo(args.station)
