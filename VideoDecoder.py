__author__ = 'aaron.anderson'

import threading
import Queue
import av
import StringIO, base64
import cStringIO
import numpy as np

class VideoDecoder(threading.Thread):
    def __init__(self,vidqueue,filename):
        super(VideoDecoder, self).__init__()
        self.appId = None
        self.running = False
        self.queue = vidqueue
        self.filename = filename
        self.container = av.open(filename)
        self.video = self.container.streams[0]

    def getHeight(self):
        return self.video.height

    def getWidth(self):
        return self.video.width

    def setAppId(self,appid):
        self.appId = appid

    def run(self):
        self.running = True
        for packet in self.container.demux(self.video):
            if self.running:
                for frame in packet.decode():
                    rgba = frame.reformat(format='rgba')
                    rgbarray = np.frombuffer(rgba.planes[0],np.uint8)
                    appid = np.fromstring(self.appId+'\x00',dtype=np.uint8)
                    dataarray = np.concatenate([appid,rgbarray])
                    self.queue.put(dataarray)
            else:
                break


