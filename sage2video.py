import cStringIO
import base64
import argparse
import av
import sys

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
        self.running = True
        self.station = station
        # self.container = av.open('/home/sad/Documents/SAGE2_Media/videos/May20thCondensedCoverage.mp4')
        self.container = av.open(station_config[self.station]['url'])
        self.video = self.container.streams[0]
        print self.video


        self.wsio = WebSocketIO("ws://localhost")

        # self.captureFrame()
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

        self.width = self.video.width
        self.height = self.video.height
        self.wsio.emit('startNewMediaStream',
                  {'id': self.appId + "|0", 'title': station_config[self.station]['title'], 'type': "image/jpeg", 'encoding': "base64",
                   'width': self.width, 'height': self.height})
        print "started app"
        self.startTransmit()



    def startTransmit(self):
        for packet in self.container.demux(self.video):
            if self.running:
                for frame in packet.decode():
                    img = frame.to_image()
                    buf = cStringIO.StringIO()
                    img.save(buf, quality=70, format='JPEG')
                    jpeg = base64.b64encode(buf.getvalue())
                    buf.close()
                    self.wsio.emit('updateMediaStreamFrame',
                                   {'id': self.appId + "|0",
                                    'state': {'src': jpeg, 'type': "image/jpeg", 'encoding': "base64"}})

    def requestNextFrame(self,data):
        pass

    def setupDisplayConfiguration(self,data):
        pass

    def stopMediaCapture(self,data):
        print "Stop media capture and exit"
        self.running = False
        sys.exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Display TV on SAGE2 Display")
    parser.add_argument('station', type=str,help="Television station (kfor,kwtv,koco,kokh")
    args = parser.parse_args()
    test = SageVideo(args.station)
