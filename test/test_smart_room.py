import unittest
import mock.GPIO as GPIO
from unittest.mock import patch, PropertyMock
from unittest.mock import Mock

from mock.adafruit_bmp280 import Adafruit_BMP280_I2C
from src.smart_room import SmartRoom
from mock.senseair_s8 import SenseairS8


class TestSmartRoom(unittest.TestCase):

    @patch.object(GPIO, "input")
    def test_check_room_occuppied(self, mock_object: Mock):
        mock_object.return_value = True
        smart_room = SmartRoom()
        self.assertTrue(smart_room.check_room_occupancy())

    @patch.object(GPIO, "input")
    def test_check_room_not_occuppied(self, mock_object: Mock):
        mock_object.return_value = False
        smart_room = SmartRoom()
        self.assertFalse(smart_room.check_room_occupancy())

    @patch.object(GPIO, "input")
    def test_is_enough_light(self, mock_photoresistor: Mock):
        mock_photoresistor.return_value = True
        smart_room = SmartRoom()
        self.assertTrue(smart_room.check_enough_light())
