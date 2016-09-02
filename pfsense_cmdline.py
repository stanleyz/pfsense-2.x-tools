import sys
from optparse import OptionParser
from ConfigParser import ConfigParser
import logging

class PfSenseOptionParser( OptionParser ):

    def __init__( self,  *args, **kwargs ):
        OptionParser.__init__( self, *args, **kwargs )

        self.add_option("-c", '--config', dest="config",
                  help="API configuration file (host name, username & password)", metavar="config.ini" )
        self.add_option("--logging", dest="logging", help="Where to log the output, default is stdout/stderr, valid values are syslog or file name", default=None, metavar='syslog/FILE_NAME')
        self.logger = logging.getLogger()

    
    def check_cmd_options( self, options ):
        if options.config is None:
            self.logger.error('%s: You must provide a config file with --config config.ini  (see: %s --help for details)' % ( self.get_prog_name(), self.get_prog_name() ))
            sys.exit( 1 )
        

    def parse_individual_options(self, options, defaults, overwrite = False, bool_keys = []):
        _parsed_options = {}
        if overwrite:
            _parsed_options = options.copy()
            _parsed_options.update(defaults)
        else:
            _parsed_options = defaults.copy()
            _parsed_options.update(options)

        return self.__unify_bools(_parsed_options, bool_keys)


    def check_required_options(self, options, required_items):
        _missed_items = []
        for item in required_items:
            if item not in options or options[item] is None:
                _missed_items.append(item)

        return _missed_items

    def __unify_bools(self, options, bool_keys = []):
        for key in bool_keys:
            if key in options and not isinstance(options[key], bool):
                if options[key].lower() in ('true', 'yes', '1'):
                    options[key] = True
                elif options[key].lower() in ('false', 'no', '0'):
                    options[key] = False

        return options
