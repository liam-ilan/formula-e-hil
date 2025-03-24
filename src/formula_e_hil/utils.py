def suspension_travel_to_potential_volts(travel_m: float):
    """Convert from suspension travel to sensor voltage output.

    Args:
        travel_m: Target travel in meters.

    """

    # From file:///Users/liamilan/Downloads/HT-011201-HT-011214%20-%20Linear%20Travel%20Sensors.pdf.
    # (100 V/m) * travel = voltage
    return 100 * travel_m


def flow_rate_to_frequency_hz(rate_litres_per_min: float):
    """Convert from flow rate to flow rate sensor frequency.

    Args:
        rate_litres_per_min: Target flow rate in litres/min.

    """

    # From https://www.adafruit.com/product/828.
    return 7.5 * rate_litres_per_min
