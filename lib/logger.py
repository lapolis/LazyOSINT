#!/usr/bin/env python3.8

import sqlite3
from sqlite3 import Error
import datetime

from colorama import Fore, Back, Style

class Logger :

    def __init__( self, sneaky=None, log_file=None):
        self.log_file = log_file
        self.sneaky = sneaky

    def print( self, msg, msgType ):
        if self.log_file:
            with open( self.log_file, 'a' ) as logFile:
                logFile.write( msg + '\n' )
        if not self.sneaky:
            print( msgType + msg + Style.RESET_ALL + Fore.RESET )

    def error( self, msg ):
        color = Fore.RED
        msg = f'XX ERROR   {datetime.datetime.now().strftime("%H:%M:%S")} --> {msg}'
        self.print( msg , color )

    def info( self, msg ):
        color = Fore.BLUE + Style.DIM
        msg = f'OO INFO    {datetime.datetime.now().strftime("%H:%M:%S")} --> {msg}'
        self.print( msg , color )

    def warning( self, msg ):
        color = Fore.YELLOW
        msg = f'## WARNING {datetime.datetime.now().strftime("%H:%M:%S")} --> {msg}'
        self.print( msg , color )

    def findings( self, msg ):
        color = Fore.GREEN + Style.BRIGHT
        msg = f'++ FOUND   {datetime.datetime.now().strftime("%H:%M:%S")} --> {msg}'
        self.print( msg , color )

class Stash :

    def __init__( self, db_name, log ):
        self.db_file = db_name
        self.log = log

    def create_connection( self ):
        conn = None
        try:
            conn = sqlite3.connect( self.db_file )
            return conn
        except Error as e:
            self.log.error(e)

        return conn

    def sql_exec( self, sql_query ):
        conn = self.create_connection()

        try:
            c = conn.cursor()
            c.execute( sql_query )
        except Error as e:
            self.log.error(e)

        conn.commit()
        conn.close()

    def sql_execcc( self, sql_query , sql_values ):
        conn = self.create_connection()

        try:
            c = conn.cursor()
            c.execute( sql_query , sql_values )
        except Error as e:
            self.log.error(e)

        conn.commit()
        conn.close()

    def db_init( self , target ):
        create_sql = []
        create_sql.append( """ PRAGMA foreign_keys = ON; """ )

        # TESTING
        create_sql.append( """ CREATE TABLE IF NOT EXISTS testing (
        target TEXT, \
        linkedin_link TEXT); """ )

        ## EMPLOYEES
        create_sql.append( """ CREATE TABLE IF NOT EXISTS employees ( \
        comp_link TEXT, \
        name TEXT PRIMARY KEY, \
        position TEXT, \
        prof_link TEXT, \
        prof_pic TEXT, \
        email TEXT, \
        FOREIGN KEY ( comp_link ) REFERENCES testing ( linkedin_link ) ); """)

        ## EMPLOYEES
        create_sql.append( """ CREATE TABLE IF NOT EXISTS potential_employees ( \
        comp_link TEXT, \
        name TEXT PRIMARY KEY, \
        position TEXT, \
        prof_link TEXT, \
        prof_pic TEXT, \
        email TEXT, \
        FOREIGN KEY ( comp_link ) REFERENCES testing ( linkedin_link ) ); """)

        # SUBDOMAINS
        create_sql.append( """ CREATE TABLE IF NOT EXISTS subdomains ( \
        domain TEXT NOT NULL, \
        subdomain TEXT NOT NULL PRIMARY KEY, \
        FOREIGN KEY ( domain ) REFERENCES testing ( target ) ); """ )

        # WHOIS
        create_sql.append( """ CREATE TABLE IF NOT EXISTS whois ( \
        hostname TEXT NOT NULL, \
        ip TEXT NOT NULL, \
        FOREIGN KEY ( ip ) REFERENCES server_info ( ip ), \
        FOREIGN KEY ( hostname ) REFERENCES subdomains ( subdomain ) ); """ )

        # SERVER INFO
        create_sql.append( """ CREATE TABLE IF NOT EXISTS server_info ( \
        ip TEXT NOT NULL PRIMARY KEY, \
        asn TEXT, \
        organization TEXT, \
        coordinate TEXT, \
        isp TEXT, \
        FOREIGN KEY ( asn ) REFERENCES asn_info ( asn ) ); """ )

        # SERVICES
        create_sql.append( """ CREATE TABLE IF NOT EXISTS services ( \
        ip TEXT NOT NULL, \
        port TEXT NOT NULL, \
        service TEXT NOT NULL, \
        FOREIGN KEY ( ip ) REFERENCES server_info ( ip ) ); """ )

        # ASN INFO
        create_sql.append( """ CREATE TABLE IF NOT EXISTS asn_info ( \
        asn TEXT NOT NULL PRIMARY KEY, \
        country TEXT NOT NULL, \
        registry TEXT NOT NULL, \
        cidr TEXT NOT NULL, \
        description TEXT, \
        registration_date TEXT NOT NULL ); """ )

        for query in create_sql:
            self.sql_exec( query )

        ################# sometimes linkedin sometime domain, sometomes both
        if 'linkedin' in target:
            self.sql_execcc( 'INSERT INTO testing( linkedin_link ) VALUES( ? )', (target,) )
        else:
            self.sql_execcc( 'INSERT INTO testing( target ) VALUES( ? )', (target,) )

    def get_column( self, table, column, compT=None, compS=None, grB=None ):
        conn = self.create_connection()

        try:
            c = conn.cursor()
            if compT and compS:
                c.execute( f'SELECT {column} FROM {table} WHERE {compT} = ?' , ( compS, ) )
            elif grB:
                c.execute( f'SELECT {column} FROM {table} GROUP BY {grB}' )
            else:
                c.execute( f'SELECT DISTINCT {column} FROM {table}' )
            result = c.fetchall()
        except Error as e:
            self.log.error(e)
            result = []

        conn.close()
        if compS or compT or grB:
            return result if result else []
        else:
            return [r[0] if result else [] for r in result]


class Fuffa :

    banner = f'''{Fore.GREEN + Style.BRIGHT}

    888                                  .d88888b.   .d8888b. 8888888 888b    888 88888888888
    888                                 d88P" "Y88b d88P  Y88b  888   8888b   888     888
    888                                 888     888 Y88b.       888   88888b  888     888
    888       8888b.  88888888 888  888 888     888  "Y888b.    888   888Y88b 888     888
    888          "88b    d88P  888  888 888     888     "Y88b.  888   888 Y88b888     888
    888      .d888888   d88P   888  888 888     888       "888  888   888  Y88888     888
    888      888  888  d88P    Y88b 888 Y88b. .d88P Y88b  d88P  888   888   Y8888     888
    88888888 "Y888888 88888888  "Y88888  "Y88888P"   "Y8888P" 8888888 888    Y888     888
                                   888
                              Y8b d88P
                               "Y88P"

    {Style.RESET_ALL + Fore.RESET}
    '''

    banner1 = f'''{Fore.GREEN + Style.BRIGHT}


    `7MMF'                                    .g8""8q.    .M"""bgd `7MMF'`7MN.   `7MF'MMP""MM""YMM
      MM                                    .dP'    `YM. ,MI    "Y   MM    MMN.    M  P'   MM   `7
      MM         ,6"Yb.  M"""MMV `7M'   `MF'dM'      `MM `MMb.       MM    M YMb   M       MM
      MM        8)   MM  '  AMV    VA   ,V  MM        MM   `YMMNq.   MM    M  `MN. M       MM
      MM      ,  ,pm9MM    AMV      VA ,V   MM.      ,MP .     `MM   MM    M   `MM.M       MM
      MM     ,M 8M   MM   AMV  ,     VVV    `Mb.    ,dP' Mb     dM   MM    M     YMM       MM
    .JMMmmmmMMM `Moo9^Yo.AMMmmmM     ,V       `"bmmd"'   P"Ybmmd"  .JMML..JML.    YM     .JMML.
                                     ,V
                                   OOb"

    {Style.RESET_ALL + Fore.RESET}
    '''
