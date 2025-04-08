from typing import Any, Dict, Optional
import urllib.request
import can
import cantools.database
import threading
import signal

LATEST_DBC_URL = "https://github.com/UBCFormulaElectric/Consolidated-Firmware/releases/download/latest/quadruna.dbc"


class Can:
    def __init__(self, bus_handle: can.BusABC, dbc_url: str = LATEST_DBC_URL):
        """Create an interface to a can bus.

        Args:
            bus_handle: python-can handle.
            dbc_url: Source of the dbc file, defaults to latest release.

        """

        self._can_bus = bus_handle

        # Parse out dbc.
        with urllib.request.urlopen(dbc_url) as response:
            dbc = response.read()
            self._db = cantools.database.load_string(dbc, database_format="dbc")

        # Build RX table.
        # This table can be accessed with:
        # self.rx_table[message_name][signal_name]
        # Eg. self.rx_table["VC_ImuAngularData"]["VC_ImuAngularVelocityYaw"]

        self.rx_table: Dict[str, Dict[str, Optional[Any]]] = {
            message.name: {signal.name: None for signal in message.signals}
            for message in self._db.messages
        }

        # Setup the exit event for the CAN RX thread.
        self._can_rx_exit_event = threading.Event()
        signal.signal(
            signal.SIGINT, lambda _signalnum, _handler: self._can_rx_exit_event.set()
        )

        def can_rx_loop():
            """Background CAN RX loop."""

            while not self._can_rx_exit_event.is_set():
                # Receive raw message, parse, and dump to rx table.
                raw_message = self._can_bus.recv(0.1)
                if raw_message is not None:
                    name = self._db.get_message_by_frame_id(
                        raw_message.arbitration_id
                    ).name
                    message = self._db.decode_message(
                        raw_message.arbitration_id, raw_message.data
                    )
                    self.rx_table[name] = message

        # Spin up thread.
        self._can_rx_thread = threading.Thread(target=can_rx_loop)

    def receive(self, message_name: str, signal_name: str) -> Optional[Any]:
        """Receive a signal given it's name the parent's message name.

        Args:
            message_name: Name of the message.
            signal_name: Name of the signal.

        Returns:
            Value of the signal.

        """

        return self.rx_table[message_name][signal_name]

    def receive_message(self, message_name: str) -> Dict[str, Optional[Any]]:
        """Receive a full message given it's name.

        Args:
            message_name: Name of the message.

        Returns:
            A dictionary mapping the name of a signal to it's value.

        """

        return self.rx_table[message_name]

    def transmit_message(self, message_name: str, signals: Dict[str, Any]):
        """Transmit a message given it's signals.

        Args:
            message_name: Name of the message.
            signals: Dictonary containing the signals to send.

        """

        message_type = self._db.get_message_by_name(message_name)
        raw_signals = message_type.encode(signals)
        raw_message = can.Message(
            arbitration_id=message_type.frame_id, data=raw_signals
        )
        self._can_bus.send(raw_message)
