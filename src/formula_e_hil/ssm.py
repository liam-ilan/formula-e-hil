import chimera_v2
from enum import Enum


class SSM:
    # ISOSPI high side and low side Chimera IDs.
    _ISOSPI_HIGH_SIDE_NAME = "SPI_ISOSPI_HS"
    _ISOSPI_LOW_SIDE_NAME = "SPI_ISOSPI_LS"

    # Maximum voltage out of the SSM DAC.
    DAC_REF_VOLTS = 5

    # DAC spi and clear (active low) Chimera IDs.
    _DAC_NAME = "SPI_DAC"
    _DAC_N_CLEAR_NAME = "GPIO_DAC_N_CLEAR"

    # Resolution of the LTC2620, 12 bits.
    _DAC_RESOLUTION = 12

    def __init__(self):
        """Create an interface to an SSM."""

        self.isospi_high_side = self._chimera_handler.spi_device(
            self._ISOSPI_HIGH_SIDE_NAME
        )
        self.isospi_low_side = self._chimera_handler.spi_device(
            self._ISOSPI_LOW_SIDE_NAME
        )

        self._chimera_handler = chimera_v2.SSM()
        self._dac_handler = self._chimera_handler.spi_device(self._DAC_NAME)

        self._chimera_handler.gpio_write(self._DAC_N_CLEAR_NAME, True)

    class Indicator(Enum):
        """Representation of an indicator LED."""

        ONE = "GPIO_INDICATOR_1"
        TWO = "GPIO_INDICATOR_2"
        THREE = "GPIO_INDICATOR_3"

    def set_indicator(self, indicator: Indicator, state: bool):
        """Write to an indicator LED.

        Args:
            indicator: Indicator LED to target.
            state: State to write.

        """

        self._chimera_handler.gpio_write(indicator.value, state)

    class Interlock(Enum):
        """Representation of an interlock peripheral."""

        ONE = "GPIO_INTERLOCK_1"
        TWO = "GPIO_INTERLOCK_2"
        THREE = "GPIO_INTERLOCK_3"
        FOUR = "GPIO_INTERLOCK_4"

    def set_interlock(self, interlock: Interlock, closed: bool):
        """Write to an interlock peripheral.

        Args:
            interlock: Interlock to target.
            closed: True if the interlock should close.

        """

        self._chimera_handler.gpio_write(interlock.value, closed)

    class DataOut(Enum):
        """Representation of a GPIO data out pin."""

        ONE = "GPIO_DOUT_1"
        TWO = "GPIO_DOUT_2"
        THREE = "GPIO_DOUT_3"
        FOUR = "GPIO_DOUT_4"

    def set_data_out(self, data_out: DataOut, state: bool):
        """Write to a data out GPIO pin.

        Args:
            data_out: GPIO data out pin to target.
            state: State to set the pin to.

        """

        self._chimera_handler.gpio_write(data_out.value, state)

    _DEBUG_LED_NAME = "GPIO_DEBUG_LED"

    def set_debug_led(self, state: bool):
        """Write to the debug LED.

        Args:
            state: State to write.

        """

        self._chimera_handler.gpio_write(self._DEBUG_LED_NAME, state)

    _BOOT_LED_NAME = "GPIO_BOOT_LED"

    def set_boot_led(self, status: bool):
        """Write to the boot LED.

        Args:
            state: State to write.

        """

        self._chimera_handler.gpio_write(self._BOOT_LED_NAME, status)

    class AnalogOut(Enum):
        """Representation of an output analog channel. Maps from channel to DAC channel id."""

        ONE = 0b00  # VOUT A.
        TWO = 0x01  # VOUT B.
        THREE = 0x02  # VOUT C.
        FOUR = 0x03  # VOUT D.
        FIVE = 0x07  # VOUT H.
        SIX = 0x06  # VOUT G.
        SEVEN = 0x05  # VOUT F.
        EIGHT = 0x04  # VOUT E.

    def dac_transmit(self, channel: AnalogOut, out_volts: float):
        """Transmit a voltage over a channel of the onboard LTC2620.

        Args:
            channel: Channel to target.
            out_volts: Voltage to output, capped at the reference voltage (SSM.DAC_REF_VOLTS).

        """

        # DAC driver for LTC2620, from the datasheet:
        # https://datasheet.ciiva.com/pdfs/VipMasterIC/IC/LITC/LITCS09782/LITCS09782-1.pdf?src-supplier=IHS+Markit

        # 0b0011 writes to input register, and updates DAC register in one command.
        command_bits = 0b0011

        # Extract channel from AnalogOut enum.
        channel_bits = channel.value

        # From V_OUT = (k / 2^N) V_REF in the datasheet.
        # ie. k = (V_OUT / V_REF) * 2^N.
        # where k is the setpoint, N is the resolution, and V_REF is the reference voltage.
        data_bits = int((out_volts / self.DAC_REF_VOLTS) * (2**self._DAC_RESOLUTION))

        # Make sure data_bits / requested output are legal.
        assert out_volts <= self.DAC_REF_VOLTS
        assert data_bits <= (2**self._DAC_RESOLUTION)

        # Build word and convert to bytes.
        # Input word format:
        # 24-----------20------------16-------------4-------------0
        # [ command (4) | channel (4) | data   (12) | UNUSED  (4) ]
        # 3 bytes long, most-significant bit to the left.
        input_word = (
            command_bits << 20 + channel_bits << 16 + data_bits << 4 + 0b0000 << 0
        )
        input_word_bytes = input_word.to_bytes(3, "big")

        # Transmit.
        self._dac_handler.transmit(input_word_bytes)
