from src.instrument_drivers.InstrumentConnection import InstrumentConnection
from src.instrument_drivers.Instrument import Instrument
from src.instrument_drivers.generic import classproperty

class MSO68B(Instrument):
    class Mode(Instrument.Mode):
        pass

    @classproperty
    def default_addresses(cls):
        addresses = set()
        addresses.add("TCPIP0::10.138.44.234::inst0::INSTR")
        return addresses
    
    def __init__(self, connection: InstrumentConnection):
        super().__init__(connection)

    def __call__(self):
        pass

    def release(self):
        pass

    def stop(self):
        pass

    def enable_img_on_trigger(self, filename, path: str = "C:/__screens/SCRIPTED", format: str = "PNG"):
        self._connection.send(f'SAVEONEV:FILED "{ path }"')
        self._connection.send(f'SAVEONEV:IMAG:FILEF { format }')
        self._connection.send(f"SAVEONEV:FILEN { filename }")
        self._connection.send("ACTONEV:LIM 1")
        self._connection.send("ACTONEV:LIMITC 10")
        self._connection.send("ACTONEV:TRIG:ACTION:SAVEIMAG:STATE 1")
        self._connection.send("ACTONEV:EN 1")

    def disable_img_on_trigger(self):
        self._connection.send("SAVEON:IMAGE OFF")
        self._connection.send("SAVEON:TRIGGER OFF")