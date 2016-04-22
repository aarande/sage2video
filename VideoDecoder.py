__author__ = 'aaron.anderson'

import threading
import Queue
import av
import StringIO, base64
import cStringIO

class VideoDecoder(threading.Thread):
    def __init__(self,vidqueue,wsio,filename):
        super(VideoDecoder, self).__init__()
        self.appId = None
        self.wsio = wsio
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
                    img = frame.to_image()
                    buf = cStringIO.StringIO()
                    img.save(buf, quality=60, format='JPEG')
                    jpeg = base64.b64encode(buf.getvalue())
                    buf.close()
                    self.wsio.emit('updateMediaStreamFrame',
                                   {'id': self.appId + "|0",
                                    'state': {'src': jpeg, 'type': "image/jpeg", 'encoding': "base64"}})
            else:
                break


