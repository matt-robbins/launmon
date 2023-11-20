import paho.mqtt.client as mqtt
from DataMuncher import DataMuncher
from datetime import datetime
import time

class MqttMuncher(DataMuncher):

    def run(self):
        while True:
            self.input.loop(timeout=1)
            if not self.connected:
                print("not connected!")
                time.sleep(1)

    @staticmethod
    def connect_cb(cli, self, flags, rc):
        self.connected = (rc == 0)
        if not self.connected:
            print("failed to connect!")
            return
        print("connected!")
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        cli.subscribe("+/sensor/current/state")

    @staticmethod
    def disconnect_cb(cli, self, rc):
        self.connected = False
        print("disconnected!")
        
    @staticmethod
    def message_cb(cli, self, msg):
        try:
            sample = float(msg.payload.decode())
        except ValueError:
            print("bad message %s" % msg.payload)
            return
        
        device = msg.topic.split("/")[0].split('-')[-1]
        loc = self.db.getDeviceLocation(device)

        if (loc is None):
            loc = device

        self.process_sample(loc,sample,datetime.utcnow())
            
    def __init__(self, host="localhost", port=1883, username=None, password=None):
        DataMuncher.__init__(self)
        self.input = mqtt.Client()
        self.connected = False

        if username and password:
            self.input.username_pw_set(username, password)

        self.input.user_data_set(self)
        self.input.on_connect = self.connect_cb
        self.input.on_message = self.message_cb
        self.input.on_disconnect = self.disconnect_cb

        self.input.connect(host, port, keepalive=60)
        self.master = False
        
if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-H", "--host", dest="host", default='localhost',
                    help="host HOST", metavar="HOST")
    parser.add_option("-p", "--port", dest="port", default=1883,
                    help="port PORT", metavar="PORT")
    
    parser.add_option("-u", "--username", dest="user", default=None,
                    help="user USER", metavar="USER")
    parser.add_option("-P", "--password", dest="password", default=None,
                    help="password PASSWORD")

    (options, args) = parser.parse_args()
    print(options.user)

    m = MqttMuncher(host=options.host,port=options.port,username=options.user,password=options.password)
    m.run()