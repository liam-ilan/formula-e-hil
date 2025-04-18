from enum import Enum
from typing import Dict

import chimera_v2


class Ssm:
    # ISOSPI high side and low side Chimera IDs.
    _ISOSPI_HIGH_SIDE_NAME = "SPI_ISOSPI_HS"
    _ISOSPI_LOW_SIDE_NAME = "SPI_ISOSPI_LS"

    # Maximum voltage out of the SSM DAC.
    # Determined via experimentation.
    DAC_REF_VOLTS = 4.33

    # DAC spi and clear (active low) Chimera IDs.
    _DAC_NAME = "SPI_DAC"
    _DAC_N_CLEAR_NAME = "GPIO_DAC_N_CLEAR"

    def __init__(self):
        """Create an interface to an SSM (Simulated Sensor Module),
        with methods that more SSM-specific than the provided Chimera interface.
        """

        self._chimera_handler = chimera_v2.SSM()

        self.isospi_high_side = self._chimera_handler.spi_device(
            self._ISOSPI_HIGH_SIDE_NAME
        )
        self.isospi_low_side = self._chimera_handler.spi_device(
            self._ISOSPI_LOW_SIDE_NAME
        )

        self._dac_handler = self._chimera_handler.spi_device(self._DAC_NAME)

        # Make sure to hold this high in order to not clear DAC data.
        self._chimera_handler.gpio_write(self._DAC_N_CLEAR_NAME, True)

    class Indicator(Enum):
        """Representation of an indicator LED."""

        ONE = "GPIO_INDICATOR_1"
        TWO = "GPIO_INDICATOR_2"
        THREE = "GPIO_INDICATOR_3"

    def set_indicator(self, indicator: Indicator):
        """Set the provided indicator on, and the rest off.

        Args:
            indicator: Indicator LED to target.

        """

        for scanned_indicator in self.Indicator:
            self._chimera_handler.gpio_write(
                scanned_indicator.value, scanned_indicator == indicator
            )

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

    class DigitalChannel(Enum):
        """Representation of a GPIO digital output pin."""

        ONE = "GPIO_DOUT_1"
        TWO = "GPIO_DOUT_2"
        THREE = "GPIO_DOUT_3"
        FOUR = "GPIO_DOUT_4"

    def set_digital(self, channel: DigitalChannel, state: bool):
        """Write to a digital output.

        Args:
            channel: Channel to target.
            state: State to set the channel to.

        """

        self._chimera_handler.gpio_write(channel.value, state)

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

    class AnalogChannel(Enum):
        """Representation of an output analog channel. Maps from ADC through hole to DAC channel id."""

        ONE = 0x00  # VOUT A.
        TWO = 0x01  # VOUT B.
        THREE = 0x02  # VOUT C.
        FOUR = 0x03  # VOUT D.
        FIVE = 0x07  # VOUT H.
        SIX = 0x06  # VOUT G.
        SEVEN = 0x05  # VOUT F.
        EIGHT = 0x04  # VOUT E.
        ALL = 0x0F

    class _DacCommand(Enum):
        """Representation of a DAC command. Maps from command description to id."""

        LOAD_CHANNEL = 0b0000
        UPDATE_CHANNEL = 0b0001
        LOAD_ONE_AND_UPDATE_ALL_CHANNELS = 0b0010
        LOAD_AND_UPDATE_CHANNEL = 0b0011
        POWER_DOWN_CHANNEL = 0b0100
        NO_OPERATION = 0b1111

    def _execute_dac_command(
        self, command: _DacCommand, channel: AnalogChannel, output_volts: float
    ):
        """Execute a SPI command on the DAC. For internal use only.

        Args:
            command: DAC command to execute.
            channel: Target channel.
            output_volts: Voltage value to use to compute the data field.

        """

        # DAC driver for LTC2620, from the datasheet:
        # https://datasheet.ciiva.com/pdfs/VipMasterIC/IC/LITC/LITCS09782/LITCS09782-1.pdf?src-supplier=IHS+Markit

        # Extract channel and command.
        command_bits = command.value
        channel_bits = channel.value

        # Ratio from output volts to ref.
        output_ratio = output_volts / self.DAC_REF_VOLTS
        assert 0 <= output_ratio <= 1

        # Data bits if we are outputing ref_volts.
        ref_volts_data_bits = 0xFFF

        # From V_OUT = (k / 2^N) V_REF in the datasheet.
        # ie. k = (V_OUT / V_REF) * 2^N.
        # where k is the setpoint, N is the resolution, and V_REF is the reference voltage.
        data_bits = int(output_ratio * ref_volts_data_bits)

        # Build word and convert to bytes.
        # Input word format:
        # 24-----------20------------16-------------4-------------0
        # [ command (4) | channel (4) | data   (12) | UNUSED  (4) ]
        # 3 bytes long, most-significant bit to the left.
        input_word_length = 3
        input_word = (command_bits << 20) + (channel_bits << 16) + (data_bits << 4)
        input_word_bytes = input_word.to_bytes(input_word_length, "big")

        # Transmit.
        self._dac_handler.transmit(input_word_bytes)

    def set_analog(self, channel: AnalogChannel, output_volts: float):
        """Transmit a voltage over an analog output channel.

        Args:
            channel: Channel to target.
            output_volts: Voltage to output, capped at the reference voltage.

        """

        self._execute_dac_command(
            self._DacCommand.LOAD_AND_UPDATE_CHANNEL, channel, output_volts
        )

    def set_analogs(self, channel_to_output_volts: Dict[AnalogChannel, float]):
        """Transmit multiple voltages over multiple channels, updating the voltages all at once.

        Args:
            channel_to_output_volts: A dictionary of channels to desired voltages.

        """

        if len(channel_to_output_volts) > 0:
            # Preload all channels with the desired voltage.
            for channel in channel_to_output_volts:
                self._execute_dac_command(
                    self._DacCommand.LOAD_CHANNEL,
                    channel,
                    channel_to_output_volts[channel],
                )

            # Update all channels in one go.
            # NOTE: the LTC2620 DAC cannot update all channels,
            # without updating the input register on at least one,
            # so we select an arbritrary channel to write a value to again.
            channel = next(iter(channel_to_output_volts))
            self._execute_dac_command(
                self._DacCommand.LOAD_ONE_AND_UPDATE_ALL_CHANNELS,
                channel,
                channel_to_output_volts[channel],
            )
