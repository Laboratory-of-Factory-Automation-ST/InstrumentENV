from src.instrument_drivers.InstrumentConnection import InstrumentConnection
from src.instrument_drivers.generic import classproperty
from enum import Enum
import logging

class Instrument:

    class Mode(Enum):
        Default = 0

    @classproperty
    def default_addresses(cls):
        raise NotImplementedError("Instrument subclass must implement 'default_addresses' property getter method")
    
    def __init__(self, connection: InstrumentConnection, mode):
        self.__connection = connection
        self.__mode = mode
    
    def __enter__(self):
        if self.__connection.is_open is False:
            self.__connection.__enter__()
        self.mode = self.__mode

        return self
    
    def __exit__(self, except_type, except_val, except_trace):
        logging.info("-> Remote lock released")
        self.stop()
        self.release()
        self.reset()

    @property
    def _connection(self):
        return self.__connection

    @property
    def mode(self):
        return self.__mode
    
    @mode.setter
    def mode(self, mode):
        self.__mode = Instrument.Mode.Default

    def reset(self):
        self.__connection.send('*RST')
