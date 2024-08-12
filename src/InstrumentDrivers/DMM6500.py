from src.InstrumentDrivers.InstrumentConnection import InstrumentConnection
from src.InstrumentDrivers.Instrument import Instrument

class DMM6500(Instrument):
    def __init__(self, connection: InstrumentConnection):
        super().__init__(connection, Instrument.InstrumentType.Datalogger)

    def release(self):
        self._connection.send('TRIG:CONT REST')

    def stop(self):
        self.reset()

    def reset(self):
        self._connection.send('*RST')
    
    def toggle_dcv_mode(self):
        self._connection.send(':SENS:FUNC "VOLT:DC"')

    def toggle_dci_mode(self):
        self._connection.send(':SENS:FUNC "AMP:DC"')
    
    def toggle_acv_mode(self):
        self._connection.send(':SENS:FUNC "VOLT:AC"')

    def toggle_aci_mode(self):
        self._connection.send(':SENS:FUNC "AMP:AC"')
    
    def set_v_range(self, range):
        self._connection.send(':SENS:VOLT:RANG ' +  str(range))

    def acquire_measurement(self, flush = True):
        meas_val = self._connection.send_query(':MEAS?', 1e-3)
        if flush:
            self._connection.send(':TRAC:CLE')
        return meas_val
