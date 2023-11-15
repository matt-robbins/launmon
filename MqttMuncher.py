
import paho.mqtt.client as mqtt
from DataMuncher import DataMuncher
from datetime import datetime

class MqttMuncher(DataMuncher):

    def run(self):
        while True:
            self.input.loop(timeout=1)
            self.checkOffline(datetime.utcnow())

    @staticmethod
    def connect_cb(cli, self, flags, rc):
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        cli.subscribe("+/sensor/current/state")

    @staticmethod
    def message_cb(cli, self, msg):
        try:
            sample = float(msg.payload.decode())
        except ValueError:
            print("bad message %s" % msg.payload)
            return
        
        device = msg.topic.split("/")[0].split('-')[-1]
        loc = self.db.getDeviceLocation(device)
        self.process_sample(loc,sample,datetime.utcnow())
            
    def __init__(self, host="localhost", port=1883):
        DataMuncher.__init__(self)
        self.input = mqtt.Client()

        self.input.user_data_set(self)
        self.input.on_connect = self.connect_cb
        self.input.on_message = self.message_cb

        self.input.connect(host, port, keepalive=60)
        
