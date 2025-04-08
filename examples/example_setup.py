from formula_e_hil import Hil
import can
import time

BMS_CAN_BUS = can.Bus(
    interface="vector", app_name="CANalyzer", channel=0, bitrate=1000000
)
SENSOR_CAN_BUS = can.Bus(
    interface="vector", app_name="CANalyzer", channel=1, bitrate=1000000
)
INVERTER_CAN_BUS = can.Bus(
    interface="vector", app_name="CANalyzer", channel=2, bitrate=1000000
)

hil = Hil(bms_bus=BMS_CAN_BUS, sensor_bus=SENSOR_CAN_BUS, inverter_bus=INVERTER_CAN_BUS)

# Pause test for correct insertion of SSMs.
# Each ssm has it's own indicator.
print("RSM Indicator:", hil.rsm_fakes.INDICATOR)
print("FSM Indicator:", hil.fsm_fakes.INDICATOR)
input("Press enter to start")

# Press apps down 50%.
hil.fsm_fakes.set_apps_percentage(50)
time.sleep(1)

# Set flow rate to 60 L/min.
hil.rsm_fakes.set_flow_rate(60)
time.sleep(1)

# Transmit "magic_message" message every 0.5 seconds over the bms can bus.
periodic_handler = hil.bms_bus.transmit_message_periodic(
    0.5, "magic_message", {"magic_signal": 10, "magic_signal_2": 10}
)
time.sleep(1)

# Check that inverter_signal is 10
assert hil.inverter_bus.receive("inverter_message", "inverter_signal") == 10
time.sleep(1)

# Stop transmit of "magic_message"
del periodic_handler
