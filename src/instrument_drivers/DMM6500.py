from src.instrument_drivers.InstrumentConnection import InstrumentConnection
from src.instrument_drivers.Instrument import Instrument
from src.instrument_drivers.generic import classproperty
from enum import Enum, auto

class DMM6500(Instrument):
    class Mode(Enum):
        DCVMeter = auto()
        DCAMeter = auto()
        R2Meter = auto()
        R4Meter = auto()

    @classproperty
    def default_addresses(cls):
        addresses = set()
        addresses.add("USB0::0x05E6::0x6500::04612268::INSTR")
        addresses.add("USB0::0x05E6::0x6500::04612414::INSTR")
        
        return addresses

    def __init__(self, connection: InstrumentConnection, mode):
        super().__init__(connection, mode)

    @Instrument.mode.setter
    def mode(self, mode: Mode):
        match (mode):
            case self.Mode.DCVMeter:
                self.toggle_dcv_mode()
            case self.Mode.DCAMeter:
                self.toggle_dci_mode()
            case _:
                pass

    def release(self):
        self._connection.send('TRIG:CONT REST')

    def stop(self):
        self.reset()

    def assert_mode(self, mode):
        mode_chk = self._connection.send_query(':SENS:FUNC?', 10e-3)
        assert mode_chk == mode, "Mode assertion error"
    
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

    def acquire_measurement(self, flush = True):
        meas_val = self._connection.send_query(':MEAS?', 1e-3)
        if flush:
            self._connection.send(':TRAC:CLE')
        return meas_val
