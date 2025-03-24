import threading
import time
from .ssm import Ssm


class RsmFakes:
    INDICATOR = Ssm.Indicator.TWO

    _FLOW_RATE_PWM = Ssm.DigitalChannel.TWO

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

        # Start flow rate pwm at 0 Hz.
        self._flow_rate_pwm_freq_hz = 0

        # Setup PWM background loop.
        def pwm_loop():
            # Run a background PWM loop.
            flow_rate_last_cycle_secs = time.time()
            while not self._pwm_exit_event.is_set():
                # Don't update flow rate if requested frequency is 0.
                if self._flow_rate_pwm_freq_hz != 0:
                    # Calculate requested period.
                    flow_rate_period_secs = 1 / self._flow_rate_pwm_freq_hz

                    # Set 50% duty cycle on flow rate PWM.
                    time_since_last_cycle_secs = time.time() - flow_rate_last_cycle_secs
                    if time_since_last_cycle_secs <= flow_rate_period_secs / 2:
                        self._ssm_handler.set_digital(self._FLOW_RATE_PWM, True)
                    elif (
                        flow_rate_period_secs / 2
                        < time_since_last_cycle_secs
                        <= flow_rate_period_secs
                    ):
                        self._ssm_handler.set_digital(self._FLOW_RATE_PWM, False)
                    else:
                        flow_rate_last_cycle_secs = time.time()

        # Spawn the pwm loop in a background thread.
        self._pwm_exit_event = threading.Event()
        self._pwm_thread = threading.Thread(target=pwm_loop)

    def __exit__(self):
        # Make sure PWM thread closes when the class destructs.
        self._pwm_exit_event.set()
        self._pwm_thread.join()

    def set_suspension_travel_left(self, value: float):
        self._ssm_handler.set_analog(self._SUSPENSION_TRAVEL_LEFT_CHANNEL, value)

    def set_suspension_travel_right(self, value: float):
        self._ssm_handler.set_analog(self._SUSPENSION_TRAVEL_RIGHT_CHANNEL, value)

    def set_rear_brake_pressure(self, value: float):
        self._ssm_handler.set_analog(self._REAR_BRAKE_PRESSURE_CHANNEL, value)

    def set_flow_rate(self, rate_litres_per_min: float):
        """Set flow rate sensor.

        Args:
            rate_litres_per_min: Litres per minute to report as the flow rate.

        """

        # From https://www.adafruit.com/product/828.
        self._flow_rate_pwm_freq_hz = 7.5 * rate_litres_per_min
