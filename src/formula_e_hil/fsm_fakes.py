from .ssm import Ssm


class FsmFakes:
    INDICATOR = Ssm.Indicator.ONE

    _FRONT_BRAKE_PRESSURE_CHANNEL = Ssm.AnalogChannel.SEVEN
    _APPS_1_CHANNEL = Ssm.AnalogChannel.FIVE
    _APPS_2_CHANNEL = Ssm.AnalogChannel.THREE
    _STEERING_CHANNEL = Ssm.AnalogChannel.TWO

    def __init__(self):
        """Create an interface to the FSM (Front-Sensor Module), through an SSM."""

        self._ssm_handler = Ssm()

        # Set the FSM indicator LED on.
        self._ssm_handler.set_indicator(self.INDICATOR, True)

    def set_steering(self, value: float):
        self._ssm_handler.set_analog(self._STEERING_CHANNEL, value)

    def set_front_brakes(self, value: float):
        self._ssm_handler.set_analog(self._FRONT_BRAKE_PRESSURE_CHANNEL, value)

    def set_apps_1(self, value: float):
        self._ssm_handler.set_analog(self._APPS_1_CHANNEL, value)

    def set_apps_2(self, value: float):
        self._ssm_handler.set_analog(self._APPS_2_CHANNEL, value)

    def set_apps(self, value: float):
        self._ssm_handler.set_analogs(
            {
                self._APPS_1_CHANNEL: value,
                self._APPS_2_CHANNEL: value,
            }
        )

    def set_left_motor_interlock(self, value: bool):
        pass

    def set_right_motor_interlock(self, value: bool):
        pass

    def set_brake_overtravel_interlock(self, value: bool):
        pass

    def set_cockpit_interlock(self, value: bool):
        pass
