from pyvisa import ResourceManager
import logging

class InstrumentConnection:
    def __init__(self, address, handler: ResourceManager, baudrate = 9600, timeout = 1000, r_terminator = '\n', w_terminator = '\n'):
        self.__address = address
        self.__handler = handler
        self.__baudrate = baudrate
        self.__timeout = timeout
        self.__read_terminator = r_terminator
        self.__write_terminator = w_terminator
        self.__connection = None

    def __enter__(self):
        try:
            self.__connection = self.__handler.open_resource(self.__address)
            self.__connection.read_termination = self.__read_terminator
            self.__connection.write_termination = self.__write_terminator
            self.__connection.baudrate = self.__baudrate
            self.__connection.timeout = self.__timeout
        except Exception as e:
            logging.error("-> Connection to instrument was unsuccessful")
            raise e
        return self

    def __exit__(self, except_type, except_val, except_trace):
        try:
            self.__connection.close()
            self.__connection = None
            logging.info("-> Connection to instrument closed")
        except:
            logging.warning("-> Connection could not be closed or is not open")

    @property
    def is_open(self):
        return self.__connection is not None

    def send(self, cmd):
        try:
            self.__connection.write(cmd)
        except:
            logging.error("-> Communication with instrument was unsuccessful")

    def send_query(self, query, await_time):
        try:
            return self.__connection.query(query, await_time)
        except:
            logging.error("-> Communication with instrument was unsuccessful")

    def handshake(self):
        return self.send_query('*IDN?', 1e-3)
