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

    """
    Two temperature sensors (specifically, two BMP280 modules), one indoor and one outdoor, are used to decide when opening/closing the window. Whenever the indoor temperature is lower than the outdoor temperature minus two degrees, the system opens the window through the servo motor; on the other hand, when the indoor temperature is greater than the outdoor temperature plus two degrees, the system closes the window. The above behavior is only triggered when both sensors measure temperatures between 18 and 30 Celsius degrees (inclusive). Otherwise, the window stays closed.

The communication with the temperature sensors happens via the I2C protocol. To read the temperature (in Celsius degrees) from the indoor sensor, access the instance variable SmartRoom.bmp280_indor and then the instance variable Adafruit_BMP280_I2C.temperature (which stores a real number representing the current temperature in Celsius degrees). Similarly, to read the temperature from the outdoor sensor, access the instance variable SmartRoom.bmp280_outdoor and then the instance variable Adafruit_BMP280_I2C.temperature. Note that the temperature sensors have already been configured in the constructor of the SmartRoom class.

To open/close the room window, the system uses a servo motor. A servo motor is a kind of DC (Direct Current) motor that, upon receiving a signal, can rotate itself to any angle from 0 to 180 degrees. We can control the servo motor by sending a PWM (Pulse-Width Modulation) signal to its pin. This means alternating a HIGH signal with a LOW signal with a given frequency. A PWM signal is characterized by a duty cycle (as well as a frequency), which is the percentage of time the signal is HIGH over a period. The duty cycle determines the angle the servo motor will rotate to.

The servo motor is connected on pin 31 (BOARD mode), operates at 50hz frequency, and a rotation of 0 degrees corresponds to the room window being fully closed, while a rotation of 180 degrees corresponds to the room window being fully open. To calculate the duty cycle corresponding to a certain angle, use the following formula:

duty cycle = (angle / 18) + 2.
The servo motor has already been configured in the constructor of the SmartRoom class. It can be controlled by passing the duty cycle (see the formula above) corresponding to the desired angle to the SmartRoom.change_servo_angle(duty_cycle: float) -> None method (already implemented).

Finally, to keep track of the window's status (i.e., open vs closed), use the boolean instance variable SmartRoom.window_open.

Requirement:

Implement SmartRoom.manage_window(self) -> None to handle the behavior of the room window.
Tip:

To mock a property like Adafruit_BMP280_I2C.temperature, you should add the following argument new_callable=PropertyMock when using the @patch.object decorator (see the slides on mocking if needed).
    
    """
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


