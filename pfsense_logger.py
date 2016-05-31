import logging
import logging.handlers
import platform

class PfSenseLogger( object ):
    level = logging.INFO

    @staticmethod
    def setupLogger ( logger_type = None, logger_name = "", level = logging.INFO ):
        logger = PfSenseLogger()
        logger['level'] = level
        if logger_type is not None and logger_type.lower() == 'syslog':
            return logger.getSysLogLogger(logger_name = logger_name)
        else:
            return logger.getStreamLogger(logger_name = logger_name)

    def getStreamLogger( self, logger_name = "", log_file = None ):
        _logger = logging.getLogger(logger_name)
        _logger.setLevel(self.level)
        _formatter = logging.Formatter("%(asctime)s %(filename)s: %(levelname)s %(message)s", "%b %d %H:%M:%S")
        if log_file is None:
            _handler = logging.StreamHandler()        
        else:
            _handler = logging.FileHandler(log_file)

        _handler.setFormatter(_formatter)
        _logger.addHandler(_handler)
        return _logger

    def getSysLogLogger( self, logger_name = "", facility = 'local6' ):
        _logger = logging.getLogger(logger_name)
        _logger.setLevel(self.level)
        _formatter = logging.Formatter("%(filename)s: %(levelname)s %(message)s", "%b %d %H:%M:%S")
        _handler = logging.handlers.SysLogHandler(address = self.__get_logger_socket(), facility = facility)

        _handler.setFormatter(_formatter)
        _logger.addHandler(_handler)

        return _logger

    def __setitem__(self, key, value):
        self.__dict__[key] = value
        
    def __get_logger_socket( self ):
        _system = platform.system().lower()
        _socket = None
        if _system == 'linux':
            _socket = '/dev/log'
        elif _system == 'os/x':
            _socket = '/var/run/syslog'
        else:
            raise Exception("Your OS %s is not supported for now!" % platform.system())

        return _socket

