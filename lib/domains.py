#!/usr/bin/env python3.8

import re
import sys
import time
import shodan
import requests
import sublist3r
from dns import resolver
from ipwhois.net import Net
from ipwhois.asn import IPASN
from bs4 import BeautifulSoup

class whoisNstuff :

    def __init__( self, log, stash ) :
        self.stash = stash
        self.log = log

    def dnsDumpster( self, domain ) :
        url = 'https://dnsdumpster.com/'
        session = requests.session()
        sess = session.get( url )

        soup = BeautifulSoup( sess.text , 'html.parser' )
        token = soup.input['value']

        headz = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0',\
                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',\
                 'Content-Type': 'application/x-www-form-urlencoded',\
                 'Origin': 'https://dnsdumpster.com',\
                 'Referer': 'https://dnsdumpster.com' }

        postStuff = { 'csrfmiddlewaretoken': token , 'targetip': domain }
        respo = session.post( url , headers=headz , cookies=sess.cookies , data=postStuff)

        respoSoup = BeautifulSoup( respo.text , 'html.parser' )

        # return [ (x.td.text) for x in doms if domain in x.td.text ]
        # return re.findall(r'(?:[a-zA-Z0-9\-]+\.)+'+domain,''.join(x.td.text for x in respoSoup.find_all( "tr" )))
        doms = re.findall(r'(?:[a-zA-Z0-9\-]+\.)+'+domain,''.join(x.td.text for x in respoSoup.find_all( "tr" )))

        if not doms:
            self.log.error('No findings in dnsDumpster')
            # sys.exit(0)
        else:
            [ self.log.findings( f'dnsDumpster found {d}' ) for d in doms ]

        for s in list( set( doms ) ):
            # sql = f'INSERT INTO subdomains( domain, subdomain ) VALUES( "{domain}" , "{s}" )'
            sqlq = 'INSERT INTO subdomains( domain, subdomain ) VALUES(?, ?)'
            sqlv = ( domain , s )
            self.stash.sql_execcc( sqlq , sqlv )
            # return list( set( doms ) )

        self.log.warning( 'If I spend more than 10 mins here just restart, sorry :)' )


    def sublister( self, domain, engine ) :
        try:
            doms = sublist3r.main( domain , \
                               40 , \
                               savefile=None , \
                               ports= None, \
                               silent=True, \
                               verbose=False, \
                               enable_bruteforce=False, \
                               engines=engine )
        except Exception as e:
            self.log.error( e )

        if not doms:
            self.log.error( f'No findings with {engine}' )
        else:
            cleanDoms = list( set( [d.replace('0-','') for dom in doms for d in dom.split('<BR>')] ))
            [ self.log.findings( f'{engine} found {d}' ) for d in cleanDoms ]
            present_subdomains = self.stash.get_column( 'subdomains', 'subdomain' )
            for s in [ x for x in cleanDoms if x not in present_subdomains ] :
                sqlq = 'INSERT INTO subdomains( domain, subdomain ) VALUES(?, ?)'
                sqlv = ( domain , s )
                self.stash.sql_execcc( sqlq , sqlv )


    def ipLookup( self ):
        subdomains = self.stash.get_column( 'subdomains', 'subdomain' )

        self.log.info('Resolving all the subdomains')

        res = resolver.Resolver()
        res.nameservers = ['1.1.1.1','1.0.0.1','8.8.8.8','8.8.4.4']

        for dom in subdomains:
            try:
                answers = res.query( dom )
                ip = list( rdata.address for rdata in answers )
            except Exception as e:
                self.log.error(e)
                ip = ['NA']

            for i in ip:
                sqlq = 'INSERT INTO whois( hostname, ip ) VALUES(?, ?)'
                sqlv = ( dom , i )
                self.stash.sql_execcc( sqlq , sqlv )
                self.log.findings(f'IP {i} found')

    def server_info( self, shodan_key ):
        sho_api = shodan.Shodan( shodan_key )
        asn_temp = []
        time2 = time.time()

        ips = self.stash.get_column( 'whois', 'ip' )

        for ip in list(set(ips)):
            sql = []

            try:
                net = Net(ip)
                obj = IPASN(net)
                info = obj.lookup()
            except Exception as e:
                info = ''
                self.log.error(e)

            # shodan magic stuff
            # lap time
            time1 = time.time()
            try:
                lap = time1 - time2
                if lap < 1 :
                    sleep_time = ( 1 - lap )
                    self.log.info( f'Sleeping {sleep_time}s waiting for shodan' )
                    time.sleep( sleep_time )
                host = sho_api.host( ip )
            except shodan.APIError as e:
                self.log.error(e)
                host = ''
            # lap time
            time2 = time.time()

            # fill up asn_info
            if info :
                asn = info["asn"]
                self.log.findings(f'ASN {asn} found for IP {ip}')

                if host:
                    # shodan found stuff
                    sqlq = 'INSERT INTO server_info( ip, asn, organization, coordinate, isp ) VALUES(?, ?, ?, ?, ?)'
                    sqlv = ( ip , asn , host["org"] , f'{host["latitude"]},{host["longitude"]}' , host["isp"] )
                    sql.append([ sqlq, sqlv ])
                    for p in host["data"]:
                        sqlq = 'INSERT INTO services( ip, port, service ) VALUES(?, ?, ?)'
                        sqlv = ( ip , p["port"] , p["data"] )
                        sql.append([ sqlq , sqlv ])

                        self.log.findings( f'Port {p["port"]} open at {ip}' )
                else:
                    self.log.warning( 'No shodan data' )
                    sql.append( [ 'INSERT INTO server_info( ip, asn ) VALUES( ?, ? )' , ( ip , asn ) ] )


                if asn not in asn_temp:
                    asn_temp.append( asn )
                    sqlq = 'INSERT INTO asn_info( asn, country, registry, cidr, description, registration_date) VALUES( ?, ?, ?, ?, ?, ? )'
                    sqlv = ( asn , info["asn_country_code"] , info["asn_registry"] , info["asn_cidr"] , info["asn_description"] , info["asn_date"] )
                    sql.append([ sqlq , sqlv ])

                for q in sql:
                    self.stash.sql_execcc( q[0] , q[1] )
