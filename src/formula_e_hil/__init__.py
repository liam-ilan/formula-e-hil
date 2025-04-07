from .fsm_fakes import FsmFakes
from .rsm_fakes import RsmFakes
from .can import Can
import can


class Hil:
    def __init__(self, can_bus_handle: can.BusABC):
        """Wrapper for the HIL system.

        Args:
            can_bus_handle: python-can CAN bus handle.

        """

        self.fsm_fakes = FsmFakes()
        self.rsm_fakes = RsmFakes()
        self.can_bus = Can(can_bus_handle)
