from src.instrument_drivers.generic import ContextGuard
from src.instrument_drivers.generic import Config
from src.instrument_drivers.InstrumentDiscovery import InstrumentDiscovery
from src.instrument_drivers.InstrumentConnection import InstrumentConnection
from src.instrument_drivers.CPX400DP import CPX400DP
from src.instrument_drivers.AFG31022 import AFG31022
import time

"""
Helper function for determining combined pin voltage thresholds
and hysteresis by applying ramping voltage
"""
def ips1050lq_dol10a1_thresholds_combined_ramp(log_level: Config.LogLevel = Config.LogLevel.INFO):
    Config.SET_LOGLEVEL = log_level
    ID = InstrumentDiscovery()
    
    ID.default_addresses = CPX400DP.default_addresses
    src_handle = ContextGuard(InstrumentConnection(ID.next_default_address, ID.connection_handler))
    
    ID.default_addresses = AFG31022.default_addresses
    gener_handle = ContextGuard(InstrumentConnection(ID.next_default_address, ID.connection_handler))

    with src_handle, gener_handle, CPX400DP(src_handle.evaluate()) as src, AFG31022(gener_handle.evaluate()) as gener:
        gener.set_wave_high_level(1, 3.3)
        gener.set_wave_offset(1, 0)
        gener.set_wave_shape(1, gener.WaveShape.DC)

        src.set_voltage(1, 9)
        src.set_voltage(2, 24)
        
        time.sleep(10)
        src.out_on(1)
        src.out_on(2)
        gener.enable_output(1)

        time.sleep(1)
        src.ramp_voltage(1, 9, 3)
        src.ramp_voltage(1, 3, 9)
        src.ramp_voltage(1, 9, 3)
        src.ramp_voltage(1, 3, 9)
        
        gener.step_dcv(1, 3.3, 0)
        gener.step_dcv(1, 0, 3.3)
        gener.step_dcv(1, 3.3, 0)
        gener.step_dcv(1, 0, 3.3)

        time.sleep(5)
        src.out_off(1)
        src.out_off(2)
        gener.disable_output(1)

"""
Helper function for determination of UVLO function voltage thresholds
and hysteresis by applying convex triangular ramp
"""
def ips1050lq_dol10a1_uvlo_convex_ramp(init_hold_time, final_hold_time, log_level: Config.LogLevel = Config.LogLevel.INFO):
    Config.SET_LOGLEVEL = log_level
    ID = InstrumentDiscovery()
    ID.default_addresses = CPX400DP.default_addresses

    src_handle = ContextGuard(InstrumentConnection(ID.next_default_address, ID.connection_handler))
    with src_handle, CPX400DP(src_handle.evaluate()) as src:
        src.set_voltage(1, 12)
        src.set_voltage(2, 3.3)
        time.sleep(10)
        src.out_on(1)
        src.out_on(2)
        time.sleep(5 if init_hold_time < 5 else init_hold_time)
        src.ramp_voltage(1, 7, 2)
        src.ramp_voltage(1, 2, 7)
        time.sleep(5 if final_hold_time < 5 else final_hold_time)
        src.out_off(2)
        src.out_off(1)

"""
Helper function for determination of UVLO function voltage thresholds
and hysteresis by appluing concave triangular ramp
"""
def ips1050lq_out16a1_uvlo_concave_ramp(init_hold_time, final_hold_time, log_level: Config.LogLevel = Config.LogLevel.INFO):
    Config.SET_LOGLEVEL = log_level
    ID = InstrumentDiscovery()
    ID.default_addresses = CPX400DP.default_addresses

    src_handle = ContextGuard(InstrumentConnection(ID.next_default_address, ID.connection_handler))
    with src_handle, CPX400DP(src_handle.evaluate()) as src:
        src.set_voltage(1, 5)
        src.set_voltage(2, 3.3)
        time.sleep(10)
        src.out_on(1)
        src.out_on(2)
        time.sleep(5 if init_hold_time < 5 else init_hold_time)
        src.ramp_voltage(1, 2, 7)
        src.ramp_voltage(1, 7, 2)
        time.sleep(5 if final_hold_time < 5 else final_hold_time)
        src.out_off(2)
        src.out_off(1)

"""
Helper function for determination of IN pin logic voltage thresholds
and hysteresis by applying convex triangular ramp
"""
def ips1050lq_dol10a1_input_convex_ramp(init_hold_time, final_hold_time, log_level: Config.LogLevel = Config.LogLevel.INFO):
    Config.SET_LOGLEVEL = log_level
    ID = InstrumentDiscovery()
    ID.default_addresses = CPX400DP.default_addresses

    src_handle = ContextGuard(InstrumentConnection(ID.next_default_address, ID.connection_handler))
    with src_handle, CPX400DP(src_handle.evaluate()) as src:
        src.set_voltage(1, 24)
        src.set_voltage(2, 5)
        time.sleep(10)
        src.out_on(1)
        src.out_on(2)
        time.sleep(5 if init_hold_time < 5 else init_hold_time)
        src.ramp_voltage(2, 5, 0)
        src.ramp_voltage(2, 0, 5)
        time.sleep(5 if final_hold_time < 5 else final_hold_time)
        src.out_off(2)
        src.out_off(1)

"""
Helper function for determination of IN pin logic voltage thresholds
and hysteresis by applying concave triangular ramp
"""
def ips1050lq_dol10a1_input_concave_ramp(init_hold_time, final_hold_time, log_level: Config.LogLevel = Config.LogLevel.INFO):
    Config.SET_LOGLEVEL = log_level
    ID = InstrumentDiscovery()
    ID.default_addresses = CPX400DP.default_addresses

    src_handle = ContextGuard(InstrumentConnection(ID.next_default_address, ID.connection_handler))
    with src_handle, CPX400DP(src_handle.evaluate()) as src:
        src.set_voltage(1, 24)
        src.set_voltage(2, 0)
        time.sleep(10)
        src.out_on(1)
        src.out_on(2)
        time.sleep(5 if init_hold_time < 5 else init_hold_time)
        src.ramp_voltage(2, 0, 5)
        src.ramp_voltage(2, 5, 0)
        time.sleep(5 if final_hold_time < 5 else final_hold_time)
        src.out_off(2)
        src.out_off(1)
