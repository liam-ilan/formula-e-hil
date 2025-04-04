def suspension_travel_to_potential_volts(travel_m: float) -> float:
    """Convert from suspension travel to sensor voltage output.

    Args:
        travel_m: Target travel in meters.

    Returns:
        Output voltage of suspension travel sensor in volts.

    """

    # From https://www.vpw.com.au/assets/brochures/HT-011211.pdf?srsltid=AfmBOop5KeZQrOQHyOzs7KeBUGRtiIAbdzRFf8_wUE9re0sPV3t8Mgt2.
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


def brake_pressure_to_potential_volts(brake_pressure_psi: float) -> float:
    """Convert from brake pressure to pressure sensor voltage output.

    Args:
        brake_pressure_psi: Target pressure in PSI.

    Returns:
        Output voltage of pressure sensor in volts.

    """

    # From direct charecterization of sensors.
    pressure_span_psi = 1000
    voltage_offset = 0.5
    potential_span_volts = 4.5 - voltage_offset
    volts_per_psi = potential_span_volts / pressure_span_psi

    return voltage_offset + volts_per_psi * brake_pressure_psi
