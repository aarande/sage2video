__author__ = 'aaron.anderson'

import threading
import Queue
import av
import StringIO, base64

class VideoDecoder(threading.Thread):
    def __init__(self,vidqueue,filename):
        super(VideoDecoder, self).__init__()
        self.queue = vidqueue
        self.filename = filename
        self.video = av.open(self.filename)

    def getHeight(self):
        return self.video.streams[0].height

    def getWidth(self):
        return self.video.streams[0].width

    def run(self):
        for packet in self.video.demux():
            for frame in packet.decode():
                if packet.stream.type == 'video':
                    img = frame.to_image()
                    buf = StringIO.StringIO()
                    img.save(buf, quality=80, format='JPEG')
                    jpeg = buf.getvalue()
                    buf.close()
                    self.queue.put(base64.b64encode(jpeg))


