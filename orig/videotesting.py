__author__ = 'aaron.anderson'

import av

container = av.open('/home/sad/sage2/public/uploads/videos/May20thCondensedCoverage.mp4')
packets = container.demux()

while True:
    packet = packets.next()
    frames = packet.decode()
    print frames

# for packet in container.demux():
#     for frame in packet.decode():
#         print type(frame)
#         try:
#             frame.to_image().save('./data/frame-%04d.jpg' % frame.index)
#         except:
#             pass
