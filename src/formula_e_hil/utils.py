def suspension_travel_to_potential_volts(travel_m: float) -> float:
    """Convert from suspension travel to sensor voltage output.

    Args:
        travel_m: Target travel in meters.

    Returns:
        Output voltage of suspension travel sensor in volts.

    """

    # From file:///Users/liamilan/Downloads/HT-011201-HT-011214%20-%20Linear%20Travel%20Sensors.pdf.
    # (100 V/m) * travel = voltage
    return 100 * travel_m


def flow_rate_to_frequency_hz(rate_litres_per_min: float) -> float:
    """Convert from flow rate to flow rate sensor frequency.

    Args:
        rate_litres_per_min: Target flow rate in litres/min.

    Returns:
        Output frequency of flow rate sensor in Hz.

    """

    # From https://www.adafruit.com/product/828.
    return 7.5 * rate_litres_per_min


def steering_angle_to_potential_volts(angle_degrees: float) -> float:
    """Convert from steering angle to steering sensor voltage output.

    Args:
        angle_degrees: Target angle in degrees.

    Returns:
        Output voltage of steering sensor in volts.

    """

    # From Quadruna steering rack values, should be identical on Quintuna.
    steering_angle_potential_offset_volts = 2.21
    steering_potential_max_volts, steering_potential_min_volts = 0.2, 3.5
    steering_potential_range_volts = (
        steering_potential_max_volts - steering_potential_min_volts
    )
    degrees_per_volts = 360 / (steering_potential_range_volts)
    return angle_degrees / degrees_per_volts + steering_angle_potential_offset_volts
