from src.instrument_drivers.InstrumentConnection import InstrumentConnection
from src.instrument_drivers.Instrument import Instrument
from src.instrument_drivers.generic import classproperty
from enum import StrEnum

class DMM6500(Instrument):
    MODE_CTRL_CMD = ":SENS:FUNC"
    
    class Mode(Instrument.Mode):
        DCVMeter = "VOLT:DC"
        DCAMeter = "VOLT:AC"
        R2PoleMeter = "RES"
        R4PoleMeter = "FRES"

    class ChanRef(Instrument.ChanRef):
        CH1_TEMP_REF = "1"
        CH2 = "2"
        CH3 = "3"
        CH4 = "4"
        CH5 = "5"
        CH6 = "6"
        CH7 = "7"
        CH8 = "8"
        CH9 = "9"
        CH10 = "10"

    @classproperty
    def default_addresses(cls):
        addresses = set()
        addresses.add("USB0::0x05E6::0x6500::04612268::INSTR")
        addresses.add("USB0::0x05E6::0x6500::04612414::INSTR")
        addresses.add("USB0::0x05E6::0x6500::04612430::INSTR")
        
        return addresses
    
    def __init__(self, connection: InstrumentConnection, mode: Mode):
        super().__init__(connection, mode)

    @property
    def mode(self):
        query = self._connection.send_query(':SENS:FUNC?', 10e-3)
        return self.Mode(query)
    
    @Instrument.mode.setter
    def mode(self, mode: Mode):
        if mode == "default":
            return
        else:
            mode_ctrl = f'{self.MODE_CTRL_CMD} "{mode}"'
            self._connection.send(mode_ctrl)
            self.assert_mode(mode)

    def release(self):
        self._connection.send('TRIG:CONT REST')

    def stop(self):
        self.reset()
    
    def toggle_dcv_mode(self):
        self._connection.send(':SENS:FUNC "VOLT:DC"')
        self.assert_mode("VOLT:DC")

    def toggle_dci_mode(self):
        self._connection.send(':SENS:FUNC "CURR:DC"')
        self.assert_mode("CURR:DC")
    
    def toggle_acv_mode(self):
        self._connection.send(':SENS:FUNC "VOLT:AC"')
        self.assert_mode("VOLT:AC")

    def toggle_aci_mode(self):
        self._connection.send(':SENS:FUNC "CURR:AC"')
        self.assert_mode("CURR:AC")
    
    def set_v_range(self, range):
        self._connection.send(':SENS:VOLT:RANG ' + str(range))

    def set_i_range(self, range):
        self._connection.send(':SENS:CURR:RANG ' + str(range))

    def route_channel(self, ref: ChanRef):
        self._connection.send(f'ROUT:CLOS (@{ ref })')

    def acquire_measurement(self, flush = True):
        meas_val = self._connection.send_query(':MEAS?', 1e-3)
        if flush:
            self._connection.send(':TRAC:CLE')
        return meas_val
