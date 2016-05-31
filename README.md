pfSense-python
==============

Some simple python scripts for programmatically changing settings in pfsense.

The code is rather ugly, but should work across most 2.x versions of python and has minimal dependencies.

Two example scripts are provided:
 - pfsense-backup: download any XML file for backup purposes
 - pfsense-updateCRL: update (modify) a Certificate Recovation List

For updateCRL, the CRL must already exist in pfSense (you can create one with no / nonsensical certificate data initially).  Once you have created it, go to the edit screen for the CRL and note down the id=[hex string] part of the URL.  This is what you must provide to --id on the command line.  Note that updateCRL will automatically append a string like '(last refresh: 2014-11-16T17:01:15.058446)' to the description to make it clear that the CRL was programmatically updated and when.  This currently cannot be turned off.

pfsense-backup usage:
```
$ pfsense-backup --help
Usage: pfsense-backup.py [options]

Options:
  -h, --help            show this help message and exit
  -c config.ini, --config=config.ini
                        API configuration file (host name, username &
                        password)
  --logging=syslog/FILE_NAME
                        Where to log the output, default is stdout/stderr,
                        valid values are syslog or file name
  --area=AREA           Backup Area: all, dnsmasq, filter, interfaces, pptpd,
                        rrddata, cron, system, sysctl, snmpd
  --no-rrd              Do not backup RRD (will result in large XML file).
                        Only applicable if --area=all.
  --no-packages         Do not backup package info. Only applicable if
                        --area=all.
  --ssl_verification=SSL_VERIFICATION
                        Whether SSL should be verified or not
  --overwrite           Command line options will overwrite same settings in
                        config file
  -o OUTPUT, --output=OUTPUT
                        Output file (default: stdout)
```

pfsense-updateCRL usage:

```
$ pfsense-backup --help
Usage: pfsense-backup.py [options]

Options:
  -h, --help            show this help message and exit
  -c config.ini, --config=config.ini
                        API configuration file (host name, username &
                        password)
  --logging=syslog/FILE_NAME
                        Where to log the output, default is stdout/stderr,
                        valid values are syslog or file name
  --area=AREA           Backup Area: all, dnsmasq, filter, interfaces, pptpd,
                        rrddata, cron, system, sysctl, snmpd
  --no-rrd              Do not backup RRD (will result in large XML file).
                        Only applicable if --area=all.
  --no-packages         Do not backup package info. Only applicable if
                        --area=all.
  --ssl_verification=yes/no
                        Whether SSL should be verified or not, valid values
                        are yes/no, true/false, 1/0
  --overwrite           Command line options will overwrite same settings in
                        config file
  -o OUTPUT, --output=OUTPUT
                        Output file (default: stdout)
```

Example usage:
```sh
   pfsense-updateCRL --config config.ini --crl README.md --ssl_verification false 
   pfsense-backup -c config.ini --area=all --no-rrd -o pfsense.all.xml
   pfsense-backup -c config.ini --area=all --no-rrd | gpg --symmetric --passphrase 'somethingdecent' -o pfsense.all.xml.gpg
```
Config file might look like:
```
[fw1]
host=fw1
port=443      
username=username
password=password
crl_id=573ba4c3feasdf5
[fw2]
host=fw2
port=443
username=api
crl_id=a573bafa387asdf2
```
