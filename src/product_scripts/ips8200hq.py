from src.instrument_drivers.generic import Exceptable
from src.instrument_drivers.generic import Config
from src.instrument_drivers.InstrumentDiscovery import InstrumentDiscovery
from src.instrument_drivers.InstrumentConnection import InstrumentConnection
from src.instrument_drivers.CPX400DP import CPX400DP
import time

"""
Helper function for determination of PGOOD pin logic voltage thresholds
and hysteresis by applying convex triangular ramp
"""
def ips8200hq_out16a1_pgood_convex_ramp(log_level: Config.LogLevel = Config.LogLevel.INFO):
    Config.SET_LOGLEVEL = log_level
    ID = InstrumentDiscovery()
    ID.default_addresses = CPX400DP.default_addresses

    src_handle = Exceptable(InstrumentConnection(ID.next_default_address, ID.connection_handler))
    with src_handle, CPX400DP(src_handle.evaluate()) as src:
        src.set_voltage(1, 24)
        time.sleep(10)
        src.out_on(1)
        time.sleep(5)
        src.ramp_voltage(1, 24, 10)
        src.ramp_voltage(1, 10, 24)
        src.out_off(1)

"""
Helper function for determination of PGOOD pin logic voltage thresholds
and hysteresis by applying concave triangular ramp
"""
def ips8200hq_out16a1_pgood_concave_ramp(log_level: Config.LogLevel = Config.LogLevel.INFO):
    Config.SET_LOGLEVEL = log_level
    ID = InstrumentDiscovery()
    ID.default_addresses = CPX400DP.default_addresses

    src_handle = Exceptable(InstrumentConnection(ID.next_default_address, ID.connection_handler))
    with src_handle, CPX400DP(src_handle.evaluate()) as src:
        src.set_voltage(1, 10)
        time.sleep(10)
        src.out_on(1)
        time.sleep(5)
        src.ramp_voltage(1, 10, 24)
        src.ramp_voltage(1, 24, 10)
        src.out_off(1)

"""
Helper function for determination of UVLO function voltage thresholds
and hysteresis by applying convex triangular ramp
"""
def ips8200hq_out16a1_uvlo_convex_ramp(log_level: Config.LogLevel = Config.LogLevel.INFO):
    Config.SET_LOGLEVEL = log_level
    ID = InstrumentDiscovery()
    ID.default_addresses = CPX400DP.default_addresses

    src_handle = Exceptable(InstrumentConnection(ID.next_default_address, ID.connection_handler))
    with src_handle, CPX400DP(src_handle.evaluate()) as src:
        src.set_voltage(1, 12)
        time.sleep(10)
        src.out_on(1)
        time.sleep(5)
        src.ramp_voltage(1, 12, 5)
        src.ramp_voltage(1, 5, 12)
        src.out_off(1)

"""
Helper function for determination of UVLO function voltage thresholds
and hysteresis by appluing concave triangular ramp
"""
def ips8200_out16a1_uvlo_concave_ramp(log_level: Config.LogLevel = Config.LogLevel.INFO):
    Config.SET_LOGLEVEL = log_level
    ID = InstrumentDiscovery()
    ID.default_addresses = CPX400DP.default_addresses

    src_handle = Exceptable(InstrumentConnection(ID.next_default_address, ID.connection_handler))
    with src_handle, CPX400DP(src_handle.evaluate()) as src:
        src.set_voltage(1, 5)
        time.sleep(10)
        src.out_on(1)
        time.sleep(5)
        src.ramp_voltage(1, 5, 12)
        src.ramp_voltage(1, 12, 5)
        src.out_off(1)

"""
Helper function for determination of IN pin logic voltage thresholds
and hysteresis by applying convex triangular ramp
"""
def ips8200hq_out16a1_input_convex_ramp(log_level: Config.LogLevel = Config.LogLevel.INFO):
    Config.SET_LOGLEVEL = log_level
    ID = InstrumentDiscovery()
    ID.default_addresses = CPX400DP.default_addresses

    src_handle = Exceptable(InstrumentConnection(ID.next_default_address, ID.connection_handler))
    with src_handle, CPX400DP(src_handle.evaluate()) as src:
        src.set_voltage(1, 24)
        src.set_voltage(2, 5)
        time.sleep(10)
        src.out_on(1)
        src.out_on(2)
        time.sleep(5)
        src.ramp_voltage(2, 5, 0)
        src.ramp_voltage(2, 0, 5)
        src.out_off(2)
        src.out_off(1)

"""
Helper function for determination of IN pin logic voltage thresholds
and hysteresis by applying concave triangular ramp
"""
def ips8200hq_out16a1_input_concave_ramp(log_level: Config.LogLevel = Config.LogLevel.INFO):
    Config.SET_LOGLEVEL = log_level
    ID = InstrumentDiscovery()
    ID.default_addresses = CPX400DP.default_addresses

    src_handle = Exceptable(InstrumentConnection(ID.next_default_address, ID.connection_handler))
    with src_handle, CPX400DP(src_handle.evaluate()) as src:
        src.set_voltage(1, 24)
        src.set_voltage(2, 0)
        time.sleep(10)
        src.out_on(1)
        src.out_on(2)
        time.sleep(5)
        src.ramp_voltage(2, 0, 5)
        src.ramp_voltage(2, 5, 0)
        src.out_off(2)
        src.out_off(1)
