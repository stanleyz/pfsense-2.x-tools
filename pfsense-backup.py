#!/usr/bin/env python

import sys

from pfsense_api import PfSenseAPI
from pfsense_cmdline import PfSenseOptionParser
from datetime import datetime
from ConfigParser import ConfigParser
from pfsense_logger import PfSenseLogger as logging

validAreas = [ 'all', 'dnsmasq', 'filter', 'interfaces', 'pptpd', 'rrddata', 'cron', 'system', 'sysctl', 'snmpd' ]
validAreasList = ', '.join(validAreas ) 

parser = PfSenseOptionParser()
parser.add_option("--area", dest="area",
                  help="Backup Area: %s" % (validAreasList ), default='all')
parser.add_option('--no-rrd', dest='noRRD', action='store_true', help='Do not backup RRD (will result in large XML file). Only applicable if --area=all.' )
parser.add_option('--no-packages', dest='noPackages', action='store_true', help='Do not backup package info. Only applicable if --area=all.' )
parser.add_option("--ssl_verification", dest="ssl_verification", help="Whether SSL should be verified or not, valid values are yes/no, true/false, 1/0", default=True, metavar="yes/no")
parser.add_option("--overwrite", dest="overwrite", default=False, help="Command line options will overwrite same settings in config file", action="store_true")
parser.add_option('-o', '--output', dest='output', help='Output file (default: stdout)' )

(options, args) = parser.parse_args()

logger = logging.setupLogger(options.logging)
parser.check_cmd_options( options )

required_items = ['host', 'username', 'password']

options_cmdline = vars(options).copy()
del options_cmdline['config']
del options_cmdline['overwrite']

configFile = ConfigParser()
configFile.read(options.config)

api = PfSenseAPI()
for section in configFile.sections():
    logger.info("Working on %s" % section)
    parsed_options = parser.parse_individual_options(configFile.items(section), options_cmdline, overwrite = options.overwrite, bool_keys = ['ssl_verification'])

    wrong_options_used = False
    missed_items = parser.check_required_options(parsed_options, required_items)

    for item in missed_items:
        logger.error('%s is reqired for entry %s' % ( item, section))
        wrong_options_used = True

    if not  parsed_options['area'] in validAreas:
        logger.error('%s is not a valid area for backup. Options are: %s' % ( parsed_options['area'], validAreasList ))
        wrong_options_used = True
    if parsed_options['area']!= 'all' and (options['noRRD '] or options['noPackages']):
        logger.error('--no-rrd and --no-packages only make sense when combined with --area=all')
        wrong_options_used = True

    if wrong_options_used:
        continue

    api['options'] = parsed_options
    api.login()

    backupArea = parsed_options['area'].lower()
    if backupArea == 'all':
            backupArea = ''
    apiData = { 
            'backuparea': backupArea,
            'Submit': 'Download configuration'
    }
    if parsed_options['noRRD']:
        apiData[ 'donotbackuprrd' ] = 'yes'
    if parsed_options['noPackages']:
        apiData[ 'nopackages' ] = 'yes'

    (rc, data, contentType) = api.call( '/diag_backup.php', 'POST',
            apiData = apiData )

    api.logout()

    if contentType != 'application/octet-stream':
        logger.error('Error: API parameters invalid (no XML file returned)')
        continue

    if parsed_options['output']:
        outputFile = open( parsed_options['output'], 'w' )
        outputFile.write( data )
        outputFile.close()
        logger.info("Wrote backup of %s to file %s" % (section, parsed_options['output']))
    else:
        print data
