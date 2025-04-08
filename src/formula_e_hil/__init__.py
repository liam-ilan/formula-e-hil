from .fsm_fakes import FsmFakes
from .rsm_fakes import RsmFakes
from .can import Can
import can


class Hil:
    def __init__(
        self, bms_bus: can.BusABC, inverter_bus: can.BusABC, sensor_bus: can.BusABC
    ):
        """Wrapper for the HIL system.

        Args:
            bms_bus: python-can CAN bus handle for bms bus.
            inverter_bus: python-can CAN bus handle for inverter bus.
            sensor_bus: python-can CAN bus handle for sensor bus.

        """

        self.fsm_fakes = FsmFakes()
        self.rsm_fakes = RsmFakes()
        self.bms_bus = Can(bms_bus)
        self.inverter_bus = Can(inverter_bus)
        self.sensor_bus = Can(sensor_bus)
