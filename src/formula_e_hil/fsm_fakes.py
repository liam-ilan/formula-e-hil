from .ssm import Ssm


class FsmFakes:
    INDICATOR = Ssm.Indicator.ONE

    _FRONT_BRAKE_PRESSURE_CHANNEL = Ssm.AnalogChannel.SEVEN
    _APPS_1_TRAVEL_CHANNEL = Ssm.AnalogChannel.FIVE
    _APPS_2_TRAVEL_CHANNEL = Ssm.AnalogChannel.THREE
    _STEERING_ANGLE_CHANNEL = Ssm.AnalogChannel.TWO

    def __init__(self):
        """Create an interface to the FSM (Front-Sensor Module), through an SSM."""

        self._ssm_handler = Ssm()

        # Set the FSM indicator LED on.
        self._ssm_handler.set_indicator(self.INDICATOR, True)

    def set_steering(self, value: float):
        self._ssm_handler.set_analog(self._STEERING_ANGLE_CHANNEL, value)

    def set_front_brakes(self, value: float):
        self._ssm_handler.set_analog(self._FRONT_BRAKE_PRESSURE_CHANNEL, value)

    def set_apps_1(self, value: float):
        self._ssm_handler.set_analog(self._APPS_1_TRAVEL_CHANNEL, value)

    def set_apps_2(self, value: float):
        self._ssm_handler.set_analog(self._APPS_2_TRAVEL_CHANNEL, value)

    def set_apps(self, value: float):
        self._ssm_handler.set_analogs(
            {
                self._APPS_1_TRAVEL_CHANNEL: value,
                self._APPS_2_TRAVEL_CHANNEL: value,
            }
        )
