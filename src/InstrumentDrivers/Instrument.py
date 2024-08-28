from src.InstrumentDrivers.InstrumentConnection import InstrumentConnection
from src.InstrumentDrivers.DAQ import Series, DAQ
from src.InstrumentDrivers.Generic import classproperty
from enum import Enum, auto
import logging

class Instrument:

    class InstrumentType(Enum):
        Datalogger = auto()
        PowerSupply = auto()
        Scope = auto()
    
    Type = InstrumentType
    MAX_USB_PORTS = 5

    @classproperty
    def default_addresses(cls):
        raise NotImplementedError("Instrument must implement 'default_addresses' property getter method")

    def __init__(self, connection: InstrumentConnection, inst_type: InstrumentType, daq_ref: str = "DAQ Reference"):
        self.__connection = connection
        self.__inst_type = inst_type
        self.__daq = {"daq_ref": Series(daq_ref)}

    @property
    def _connection(self):
        return self.__connection
    
    @property
    def type(self):
        return self.__inst_type

    def __enter__(self):
        return self
    
    def __exit__(self, except_type, except_val, except_trace):
        logging.info("-> Remote lock released")
        self.stop()
        self.release()

    def add_daq(self, daq_capture: DAQ.Capture):
        match (daq_capture):
            case DAQ.Capture.AC.Voltage:
                pass
            case _:
                pass
