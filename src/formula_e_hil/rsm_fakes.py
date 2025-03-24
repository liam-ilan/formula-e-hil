from .ssm import Ssm


class RsmFakes:
    INDICATOR = Ssm.Indicator.TWO

    _FLOW_RATE_PWM = Ssm.DataOut.TWO

    _SUSPENSION_TRAVEL_RIGHT_CHANNEL = Ssm.AnalogChannel.SEVEN
    _SUSPENSION_TRAVEL_LEFT_CHANNEL = Ssm.AnalogChannel.SIX
    _REAR_BRAKE_PRESSURE_CHANNEL = Ssm.AnalogChannel.FIVE
    _PUMP_POTENTIOMETER_CONTROL_CHANNEL = Ssm.AnalogChannel.THREE
    _PUMP_GROUND_CHANNEL = Ssm.AnalogChannel.TWO
    _LOAD_CELL_NEGATIVE_CHANNEL = Ssm.AnalogChannel.FOUR
    _LOAD_CELL_POSITIVE_CHANNEL = Ssm.AnalogChannel.ONE

    def __init__(self):
        """Create an interface to the RSM (Rear-Sensor Module), through an SSM."""

        self._ssm_handler = Ssm()

        # Set the RSM indicator LED on.
        self._ssm_handler.set_indicator(self.INDICATOR, True)

        # Tie the pump ground channel to ground.
        self._ssm_handler.set_analog(self._PUMP_GROUND_CHANNEL, 0)

    def set_suspension_travel_left(self, value: float):
        self._ssm_handler.set_analog(self._SUSPENSION_TRAVEL_LEFT_CHANNEL, value)

    def set_suspension_travel_right(self, value: float):
        self._ssm_handler.set_analog(self._SUSPENSION_TRAVEL_RIGHT_CHANNEL, value)

    def set_rear_brake_pressure(self, value: float):
        self._ssm_handler.set_analog(self._REAR_BRAKE_PRESSURE_CHANNEL, value)
