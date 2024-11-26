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
    @patch.object(GPIO, "input")
    @patch.object(GPIO, "output") #led
    def test_room_is_occupied_and_not_enough_light(self, mock_led: Mock, mock_sensors: Mock):
        mock_sensors.side_effect = [True, False] #infared, photoresistor
        smart_room = SmartRoom()
        smart_room.manage_light_level()
        mock_led.assert_called_with(smart_room.LED_PIN, GPIO.HIGH)
        self.assertTrue(smart_room.light_on)

    # When the room is occupied and the there is enough light, the light should not be turned on
    @patch.object(GPIO, "input")
    @patch.object(GPIO, "output")  # led
    def test_room_is_occupied_and_enough_light(self, mock_led: Mock, mock_sensors: Mock):
        mock_sensors.side_effect = [True, True]
        smart_room = SmartRoom()
        smart_room.light_on = False
        smart_room.manage_light_level()
        mock_led.assert_called_with(smart_room.LED_PIN, GPIO.LOW)
        self.assertFalse(smart_room.light_on)

    # When the room is not occupied, the light should not be turned on
    @patch.object(GPIO, "input")
    @patch.object(GPIO, "output")
    def test_room_is_not_occupied(self, mock_led: Mock, mock_sensors: Mock):
        mock_sensors.side_effect = [False, False]
        smart_room = SmartRoom()
        smart_room.light_on = False
        smart_room.manage_light_level()
        mock_led.assert_called_with(smart_room.LED_PIN, GPIO.LOW)
        self.assertFalse(smart_room.light_on)

    @patch.object(Adafruit_BMP280_I2C, "temperature", new_callable=PropertyMock)
    def test_open_window(self, mock_temperature: Mock):
        smart_room = SmartRoom()
        mock_temperature.side_effect = [20, 25] #indoor, outdoor
        smart_room.manage_window()
        self.assertTrue(smart_room.window_open)

    @patch.object(Adafruit_BMP280_I2C, "temperature", new_callable=PropertyMock)
    def test_close_window(self, mock_temperature: Mock):
        smart_room = SmartRoom()
        mock_temperature.side_effect = [25, 20]
        smart_room.manage_window()
        self.assertFalse(smart_room.window_open)

    @patch.object(Adafruit_BMP280_I2C, "temperature", new_callable=PropertyMock)
    def test_manage_window_below_18(self, mock_temperature: Mock):
        smart_room = SmartRoom()
        mock_temperature.side_effect = [15, 20]
        smart_room.manage_window()
        self.assertFalse(smart_room.window_open)

    @patch.object(Adafruit_BMP280_I2C, "temperature", new_callable=PropertyMock)
    def test_manage_window_above_30(self, mock_temperature: Mock):
        smart_room = SmartRoom()
        mock_temperature.side_effect = [35, 20]
        smart_room.manage_window()
        self.assertFalse(smart_room.window_open)

    @patch.object(SenseairS8, "co2")
    @patch.object(GPIO, "output")
    def test_monitor_air_quality_turn_on_fan(self, mock_output: Mock, mock_co2: Mock):
        smart_room = SmartRoom()
        mock_co2.return_value = 800
        smart_room.monitor_air_quality()
        mock_output.assert_called_with(smart_room.FAN_PIN, GPIO.HIGH)
        self.assertTrue(smart_room.fan_on)

    @patch.object(SenseairS8, "co2")
    @patch.object(GPIO, "output")
    def test_monitor_air_quality_turn_off_fan(self, mock_output: Mock, mock_co2: Mock):
        smart_room = SmartRoom()
        mock_co2.return_value = 499
        smart_room.monitor_air_quality()
        mock_output.assert_called_with(smart_room.FAN_PIN, GPIO.LOW)
        self.assertFalse(smart_room.fan_on)


