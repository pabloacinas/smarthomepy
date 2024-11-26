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

    @patch.object(GPIO, "input")
    def test_is_not_enough_light(self, mock_photoresistor: Mock):
        mock_photoresistor.return_value = False
        smart_room = SmartRoom()
        self.assertFalse(smart_room.check_enough_light())

    #When the room is occupied and the there is not enough light, the light should be turned on
    @patch.object(GPIO, "output") #led
    @patch.object(GPIO, "input") #infrared
    @patch.object(GPIO, "input") #photoresistor
    def test_room_is_occupied_and_not_enough_light(self, mock_photoresistor: Mock, mock_infrared: Mock, mock_led: Mock):
        mock_photoresistor.return_value = False
        mock_infrared.return_value = True
        smart_room = SmartRoom()
        smart_room.manage_light_level()
        mock_led.assert_called_with(smart_room.LED_PIN, GPIO.HIGH)
        self.assertTrue(smart_room.light_on)


