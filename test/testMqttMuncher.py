import unittest
from MqttMuncher import MqttMuncher

class TestProcessor(unittest.TestCase):
    def setUp(self):
        self.muncher = MqttMuncher(username="launmon",password="monny")

    def test_connection(self):
        return True