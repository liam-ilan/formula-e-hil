from .ssm import Ssm
from . import utils


class FsmFakes:
    INDICATOR = Ssm.Indicator.ONE

    _BRAKE_PRESSURE_CHANNEL = Ssm.AnalogChannel.SEVEN
    _APPS_1_TRAVEL_CHANNEL = Ssm.AnalogChannel.FIVE
    _APPS_2_TRAVEL_CHANNEL = Ssm.AnalogChannel.THREE
    _STEERING_ANGLE_CHANNEL = Ssm.AnalogChannel.TWO

    def __init__(self):
        """Create an interface to the FSM (Front-Sensor Module), through an SSM."""

        self._ssm_handler = Ssm()

        # Set the FSM indicator LED on.
        self._ssm_handler.set_indicator(self.INDICATOR)

    def set_steering_angle(self, angle_degrees: float):
        """Set steering angle.

        Args:
            angle_degrees: Desired angle in degrees.

        """

        self._ssm_handler.set_analog(
            self._STEERING_ANGLE_CHANNEL,
            utils.steering_angle_to_potential_volts(angle_degrees),
        )

    def set_brake_pressure(self, pressure_psi: float):
        """Set brake pressure.

        Args:
            pressure_psi: Desired pressure in PSI.

        """

        potential_volts = utils.brake_pressure_to_potential_volts(pressure_psi)
        self._ssm_handler.set_analog(self._BRAKE_PRESSURE_CHANNEL, potential_volts)

    def set_apps_1_percentage(self, percentage: float):
        """Set primary apps percentage.

        Args:
            percentage: Desired percentage.

        """

        self._ssm_handler.set_analog(
            self._APPS_1_TRAVEL_CHANNEL,
            utils.apps_percentage_to_potential_volts(percentage),
        )

    def set_apps_2_percentage(self, percentage: float):
        """Set secondary apps percentage.

        Args:
            percentage: Desired percentage.

        """

        self._ssm_handler.set_analog(
            self._APPS_2_TRAVEL_CHANNEL,
            utils.apps_percentage_to_potential_volts(percentage),
        )

    def set_apps_percentage(self, percentage: float):
        """Set all apps percentage.

        Args:
            percentage: Desired percentage.

        """

        self._ssm_handler.set_analogs(
            {
                self._APPS_1_TRAVEL_CHANNEL: utils.apps_percentage_to_potential_volts(
                    percentage
                ),
                self._APPS_2_TRAVEL_CHANNEL: utils.apps_percentage_to_potential_volts(
                    percentage
                ),
            }
        )
