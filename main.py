#!/usr/bin/env python3.8

import os
import re
import sys
import shutil
import string
import getpass
import hashlib
import argparse
import configparser
import concurrent.futures
from urllib.parse import quote
from platform import python_version

from lib.domains import whoisNstuff
from lib.logger import Stash, Logger, Fuffa
from lib.linkedinCompanyScraper import LinkedIn

def fPath( name , t ):
    out_fold = os.path.join( os.getcwd(), 'out' )
    if not os.path.isdir( out_fold ):
        os.makedirs( out_fold )

    if name:
        valid_chars = f'._{string.ascii_letters}{string.digits}'
        myName = ''.join(c for c in name if c in valid_chars)
        fp = os.path.join( out_fold , myName )
        return fp if t == 'tmp' else fp + '.db' if t == 'db' else fp + '.lazyLog'
    else:
        return None


def main() :
    os.system('clear')

    if python_version()[0:3] < '3.8':
        print('\n\nMake sure you have Python 3.8+ installed, quitting.\n\n')
        sys.exit(1)


    parser = argparse.ArgumentParser( description='This is the the full list of availables flags.' )
    parser.add_argument( '-f', '--db_file', help='Name of the sqlite database used to store any retreived information.\n', required=True )
    parser.add_argument( '-s', '--sneaky', action='store_true', help='Do not show any LOG on screen.\n')
    parser.add_argument( '-d', '--domain', help='Target domain.\n')
    parser.add_argument( '-l', '--log_file', help='Name of file where to write all the logs.\n')
    # parser.add_argument( '-r', '--report_name', help='Name of the docx file to generate.\n')
    parser.add_argument( '-e', '--email', help='Linkedin registered email address.\n')
    parser.add_argument( '-p', '--password', help='Linkedin password. If omitted and arg -u is given, you will be prompted fro a password.\n')
    parser.add_argument( '-u', '--linkedin_url', help='Target company\'s Linkedin Profile. Example --> https://www.linkedin.com/company/niceCompanyName/\n')
    parser.add_argument( '-N', '--no_resolv', action='store_true', help='Do NOT resolv subdomains nor check for open ports.\n')
    
    parser.add_argument( '-B', '--beeep_n_pause_captcha', action='store_true', help='Pause when LazyOSINT hits reCAPTCHA and Beep!\n')
    parser.add_argument( '-b', '--pause_captcha', action='store_true', help='Pause when LazyOSINT hits reCAPTCHA, no beep.\n')
    parser.add_argument( '-r', '--resume_linkedin', action='store_true', help='Resume an interrupted LinkedIn scraper - Need to specify the exact same LinkedIn url (-u).\n')

    args = parser.parse_args()

    # report_name = fPath( args.report_name, 'doc' )
    db_file = fPath( args.db_file, 'db' )
    log_file = fPath( args.log_file, 'log' )

    log = Logger( args.sneaky, log_file ) if log_file else Logger( args.sneaky )

    if not args.sneaky:
        print( Fuffa.banner1 )

    stash = Stash( db_file, log )

    domain = args.domain
    if domain :
        # dom_reg = r'(?:^https:\/\/|^http:\/\/|^\/|^)(\w*?\.\w*\.?\w*)'
        dom_reg = r'(?:^https:\/\/|^http:\/\/|^\/|^)(\w*?\.?\w*\.?[\w\-\.]*)'
        found = re.search( dom_reg, domain )
        if found :
            domain = found.group(1)
            stash.db_init( domain )
        else :
            log.error( f'The domain doesn\'t look like a domain.' )
            sys.exit(1)

    ## sanitize linkedin url
    linkedin_url = args.linkedin_url
    if linkedin_url:
        stash.db_init( linkedin_url )
        urlecoded = quote( linkedin_url , safe=':/' )
        temp_file = fPath( f'.{str(hashlib.sha1( linkedin_url.encode() ).hexdigest())}' , 'tmp' )

        if 'https://www.linkedin.com/' in urlecoded :
            linkedin_url = urlecoded
        else :
            log.error( f'The linkedin company\'s url doesn\'t look right.' )
            linkedin_url = None
            sys.exit(1)

    if not args.no_resolv :
        SHODAN_API_KEY = None
        config = configparser.ConfigParser()
        config.read( os.getcwd() + '/API_KEYS.conf' )
        if 'SHODAN' in config:
            SHODAN_API_KEY = config['SHODAN']['key']
            lenSH = len( SHODAN_API_KEY )
            if lenSH != 32 :
                log.error( 'Shodan api key wrong lenght.' )
                sys.exit(1)
            elif not SHODAN_API_KEY.isalnum() :
                log.error( 'Nice try, put a correct Shodan api key.' )
                sys.exit(1)
        else:
            log.error( 'Please write your shodan api key in API_KEYS.conf' )
            sys.exit(1)


    t = concurrent.futures.ThreadPoolExecutor(max_workers=30)

    if linkedin_url :
        email = args.email
        password = args.password

        if not email:
            email = input( 'Email: ')

        email_reg = r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
        x = re.fullmatch( email_reg , email )
        if not x :
            log.error( f'The email is not valid.' )
            sys.exit(1)

        if not password:
            password = getpass.getpass( prompt='Password: ' )

        lnkd = LinkedIn( log, stash, linkedin_url, temp_file, res=args.resume_linkedin, pause=args.pause_captcha, beeppause=args.beeep_n_pause_captcha )
        
        ### linkedinT = [ t.submit( lnkd.scrapeThoseEmployeez, email, password, linkedin_url ) ]
        lnkd.scrapeThoseEmployeez( email, password )

    if domain :
        doms = whoisNstuff( log, stash )
        # threads = [ t.submit( doms.dnsDumpster, domain ) ]
        engines=['baidu','yahoo','google','bing','ask','netcraft','virustotal','threatcrow','ssl','passivedns']
        threads = [ t.submit( doms.sublister, domain, e ) for e in engines ]
        threads.append( t.submit( doms.dnsDumpster, domain ) )
        x = [ x.result() for x in concurrent.futures.as_completed( threads ) ]

        if not args.no_resolv :
            t.submit( doms.ipLookup ).result()
            t.submit( doms.server_info, SHODAN_API_KEY ).result()

    if linkedin_url :
        lin = [ x.result() for x in concurrent.futures.as_completed( linkedinT ) ]


    # if report_name:
    #     rep = Reporting( db_file, report_name, log )
    #     rep.writeReport()

if __name__ == '__main__' :
    main()
