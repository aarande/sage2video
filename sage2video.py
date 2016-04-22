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
station_config = {'kfor':{'url':'http://localhost:8090/ch4.flv',
                          'title':'KFOR Ch 4 (NBC)'},
                  'koco': {'url': 'http://localhost:8090/ch5.flv',
                           'title': 'KOCO Ch 5 (ABC)'},
                'kwtv': {'url': 'http://localhost:8090/ch9.flv',
                         'title': 'KWTV Ch 9 (CBS)'},
                'kokh': {'url': 'http://localhost:8090/ch12.flv',
                         'title': 'KOKH Ch 12 (FOX)'}
                  }

class SageVideo(object):
    def __init__(self,station):
        super(SageVideo, self).__init__()
        self.station = station
        self.wsio = WebSocketIO("ws://localhost")
        self.queue = Queue.Queue()
        self.video = VideoDecoder(self.queue,self.wsio,station_config[self.station]['url'])
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
        self.appId = data['UID']
        self.video.setAppId(data['UID'])
        self.width = self.video.getWidth()
        self.height = self.video.getHeight()

        self.wsio.emit('startNewMediaStream',
                  {'id': self.appId + "|0", 'title': station_config[self.station]['title'], 'type': "image/jpeg", 'encoding': "base64",
                   'width': self.width, 'height': self.height})
        self.video.start()
        print "started app"

    def requestNextFrame(self,data):
        pass


    def setupDisplayConfiguration(self,data):
        pass

    def stopMediaCapture(self,data):
        print "Stop media capture and exit"
        self.video.running = False
        sys.exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Display TV on SAGE2 Display")
    parser.add_argument('station', type=str,help="Television station (kfor,kwtv,koco,kokh")
    args = parser.parse_args()
    test = SageVideo(args.station)
