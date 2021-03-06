#!/usr/bin/env python

from HTMLParser import HTMLParser
from httplib import HTTPConnection
from httplib import HTTPSConnection
from urllib import urlencode

import email, email.mime, email.mime.base, email.mime.multipart, email.mime.application, email.mime.text

class PfSenseLoginFailure( Exception ):
    pass

class PfSenseFormParser(HTMLParser):
    csrf = None
    formEncoding = 'application/x-www-form-urlencoded'

    def getAttr( self, attrs, search ):
        for (name, value) in attrs:
            if name == search:
                return value
        return None

    def handle_starttag( self, tag, attrs ):
        if tag == 'input':
            if self.getAttr( attrs, 'type') == 'hidden':
                if self.getAttr( attrs, 'name') == '__csrf_magic':
                    self.csrf = self.getAttr( attrs, 'value' )
        elif tag == 'form':
            enctype = self.getAttr( attrs, 'enctype' )
            if enctype is not None:
                self.formEncoding = enctype

    def parse( self, filelike ):
      self.csrf = None

      response = None
      while response is None or len( response ) > 0:
        response = filelike.read( 2048 )
        self.feed( response )


class PfSenseAPI( object ):
    cookies = dict()
    options = None

    def __init__( self, options = dict() ):
        self.options = options

    def __setitem__(self, key, value):
        if key.lower() == 'options':
            self.options = value
        else:
            raise Exception("Only options is accpeted!!")

    def connection( self ):
        return conn

    def login( self ):
        (rc, resultPage, contentType) = self.call( '/index.php', 'POST', 
            { 'usernamefld': self.options['username'], 
              'passwordfld': self.options['password'],
              'login': 'Login'
            } )

        if rc != 302:
            raise PfSenseLoginFailure( "Login failure - check username and password" )

    def logout( self ):
        (rc, result, contentType ) = self.call( '/index.php', 'GET', {'logout': 'yes'} )
        return True

    def __setCookies( self, response ):
        for (name, value) in response.getheaders():
            if name == 'set-cookie':
                cookieInfo = value.split( '=', 2 )
                if len( cookieInfo ) < 2:
                    continue
                cookieData = cookieInfo[ 1 ].split( ';', 2 )
                self.cookies[ cookieInfo[ 0 ] ] = cookieData[ 0 ]

    def __insertCookies( self, headers ):
        cookieHeader = []
        for (name, value) in self.cookies.items():
            cookieHeader += [ '%s=%s' % (name, value) ]
        headers[ 'Cookie' ] = '; '.join( cookieHeader )
        return headers

    def __buildGETUrl( self, url, getData ):
        if len( getData.items() ) > 0:
            if '?' in url:
                if url[ -1 ] != '&':
                    url += '&'
            else:
                url += '?'
            url += urlencode( getData )

        return url

    def call( self, url, method, apiData = dict(), itemData = dict()):
        # Create SSL context first based on if SSL connection should be verified
        import ssl

        try:
            if self.options['ssl_verification']:
                _ssl_context = ssl._create_default_https_context
            else:
                _ssl_context = ssl._create_unverified_context
        except AttributeError:
            # pass legacy python which doesn't verify https connection
            pass
        else:
            ssl._create_default_https_context = _ssl_context

        conn = HTTPSConnection( self.options['host'], self.options['port'])
        conn.connect()
        headers = {
            'Host': self.options['host'],
            'Referer': 'https://%s/' % ( self.options['host'])
        }

        conn.request( 'GET', self.__buildGETUrl( url, itemData ), headers=self.__insertCookies( headers ) )
        initialResponse = conn.getresponse()
        self.__setCookies( initialResponse )
       
        formParser = PfSenseFormParser()
        formParser.parse( initialResponse )
        
        # Step2: build form apiData and call  the actual API
        if formParser.csrf: apiData[ '__csrf_magic' ] = formParser.csrf
        apiData.update( itemData )

        if method == 'GET':
            conn.request( 'GET',  self.__buildGETUrl( url, apiData ), headers=self.__insertCookies( headers ) )
        elif method == 'POST':
            finalHeaders = self.__insertCookies( headers )

            if formParser.formEncoding == "application/x-www-form-urlencoded":
                headers[ "Content-type" ] = formParser.formEncoding
                postEncoded = urlencode( apiData )

                conn.request( 'POST', url, headers=finalHeaders, body=postEncoded )
            else:
                # Multipart
                mime = email.mime.multipart.MIMEMultipart( 'form-data' )
                for (name, data) in apiData.items():
                    if isinstance( data, email.mime.base.MIMEBase ):
                        attachment = data
                    else:
                        attachment = email.mime.text.MIMEText( data, 'plain' )

                    if attachment.get_param( 'filename' ):
                        attachment.add_header('Content-Disposition', 'form-data', name=name, filename=attachment.get_param( 'filename' ) )
                        attachment.del_param( 'filename' )
                    else:
                        attachment.add_header('Content-Disposition', 'form-data', name=name )

                    mime.attach( attachment )

                body = mime.as_string()
                # Content-type from mime now has the embedded boundary tag that is required for the multipart stuff to work
                headers[ "Content-type" ] = mime.get( 'Content-type' )
                conn.request( 'POST', url, headers=finalHeaders, body=body )

        else:
            raise ArgumentError( 'Bad API call: method must be either POST or GET' )
            
        finalResponse = conn.getresponse()
        self.__setCookies( finalResponse )

        return (finalResponse.status, finalResponse.read(), finalResponse.getheader( 'Content-type', 'text/html' ))
