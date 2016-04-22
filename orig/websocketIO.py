import websocket
import thread
import time
import json


class websocketIO:
    def __init__(self, address):
        self.ws = None
        self.openCallback = None
        self.address = address;
        self.messages = {}

    def open(self, callback):
        print self.address

        self.ws = websocket.WebSocketApp(self.address, on_message=self.on_message, on_error=self.on_error,
                                         on_close=self.on_close)
        self.openCallback = callback

        self.ws.on_open = self.on_open;

        try:
            self.ws.run_forever()
        except KeyboardInterrupt:
            print("exit")

    def on_open(self, ws):
        thread.start_new_thread(self.openCallback, ())

    def on_message(self, ws, message):
        # print type(message) is str
        #print type(message) is list
        #print type(message) is dict

        if isinstance(message, str):
            msg = json.loads(message)
            if msg['f'] in self.messages:
                self.messages[msg['f']](msg['d'])
        else:
            print "Error: message is not a binary string"

    def on_error(self, ws, error):
        print "ERROR:"
        print error

    def on_close(self, ws):
        print "CLOSED"

    def run(self, *args):
        self.ws.on_open = args[0]

    def on(self, name, callback):
        self.messages[name] = callback

    def emit(self, name, data):
        message = {'f': name, 'd': data}

        self.ws.send(json.dumps(message))

    # binary
    # self.ws.send_binary(message)
	