#!/usr/bin/env python

import sys

from pfsense_api import PfSenseAPI
from datetime import datetime

from pfsense_cmdline import PfSenseOptionParser
from ConfigParser import ConfigParser
from pfsense_logger import PfSenseLogger as logging

parser = PfSenseOptionParser()

parser.add_option("--id", dest="crl_id", help="ID of the CRL to update")
parser.add_option("--name", dest="name", help="Descriptive name of the CRL", default="Imported CRL")
parser.add_option("--crl", dest="crl", help="File containing CRL in PEM format", metavar="CRL_FILE")
parser.add_option("--ssl_verification", dest="ssl_verification", help="Whether SSL should be verified or not, valid values are yes/no, true/false, 1/0", default=True, metavar="yes/no")
parser.add_option("--overwrite", dest="overwrite", default=False, help="Command line options will overwrite same settings in config file", action="store_true")

(options, args) = parser.parse_args()

parser.check_cmd_options( options )
logger = logging.setupLogger(options.logging)

required_items = ['crl_id', 'crl', 'host', 'username', 'password']

options_cmdline = vars(options).copy()
del options_cmdline['config']
del options_cmdline['overwrite']

configFile = ConfigParser()
configFile.read(options.config)

api = PfSenseAPI()
for section in configFile.sections():
    logger.info("Working on %s" % section)
    parsed_options = parser.parse_individual_options(configFile.items(section), options_cmdline, overwrite = options.overwrite, bool_keys = ['ssl_verification'])

    required_items_missed = False
    missed_items = parser.check_required_options(parsed_options, required_items)

    for item in missed_items:
        logger.error('%s is reqired for entry %s' % ( item, section))
        required_items_missed = True

    if required_items_missed:
        continue

    api['options'] = parsed_options
    api.login()

    if not os.path.isfile(parsed_options['crl']):
        logger.error('%s does not exist?' % parsed_options['crl'])
        continue
    try:
        crlFile = open(parsed_options['crl'], 'r')
        crlData = crlFile.read()
        crlFile.close()
    except:
        logger.error("Error while read CRL data from file %s" % parsed_options['crl'])
        continue

    (rc, data, contentType) = api.call( '/system_crlmanager.php', 'POST',
            apiData = { 
              'method': 'existing',
              'descr': '%s (last refresh: %s)' % (options.name, datetime.now().isoformat()),
              'crltext': crlData,
              'submit': 'Save'
            },
            itemData = {
              'id': parsed_options['crl_id'],
              'act': 'editimported'
            })

    api.logout()

    if rc == 302:
        logger.info('CRL Update successful for %s' % (section))
    else:
        logger.info('CRL Update failed for %s' % ( section))
