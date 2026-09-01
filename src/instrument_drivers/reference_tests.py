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
def pin_thresholds_reference_test(vcc, vdd, log_level: Config.LogLevel = Config.LogLevel.INFO):
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
