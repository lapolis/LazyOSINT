#!/usr/bin/env python3

import os
import re
import time
import tweepy
import hashlib 
import argparse
import datetime
import requests
import configparser
from bs4 import BeautifulSoup
from selenium import webdriver
from platform import python_version
from colorama import Fore, Back, Style
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

os.system('clear')

if python_version()[0:3] < '3.7':
	print('\n\nMake sure you have Python 3.7+ installed, quitting.\n\n')
	exit(1)

parser = argparse.ArgumentParser()
parser.add_argument( '-f', '--firefox_binary', help='Specify the full path of Firefox/Firefox-esr. Not the symbolic link!\n' )
args = parser.parse_args()

# selenium/requests stuff
fir_bin = args.firefox_binary
headers = {
	'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0',
}

# cause colours matter!!
G = f'{Fore.GREEN}{Style.BRIGHT}'
GG = f'{Fore.BLACK}{Back.GREEN}'
Y = f'{Fore.YELLOW}'
R = f'{Fore.RED}{Style.BRIGHT}'
C = f'{Fore.CYAN}{Style.BRIGHT}'
RES = f'{Style.RESET_ALL}'

# general stuff
LOCATION = os.getcwd()
STARTED = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

# doing some mess on your folder
l_list = []
PASTE_FILE = f'{LOCATION}/pasteList.txt'
if os.path.exists( PASTE_FILE ):
	with open( PASTE_FILE , 'r' ) as rf:
		l_list = rf.read().split('\n')
else :
	with open( PASTE_FILE , 'w' ) as wf:
		wf.write('')

ERRORS_FILE = f'{LOCATION}/errors.txt'
if not os.path.exists( ERRORS_FILE ):
	with open( ERRORS_FILE , 'w' ) as wf :
		wf.write('')

DUMP_FOLDER = f'{LOCATION}/dumps/'
if not os.path.exists( DUMP_FOLDER ):
	os.mkdir( f'{DUMP_FOLDER}' )

API_CONF_FILE = f'{LOCATION}/tweet_API.conf'
if not os.path.exists( API_CONF_FILE ):
	print( f'[{R}E{RES}] tweet_API.conf {R}MISSING{RES}!' )
	print( f'[{R}E{RES}] It might be good if you {R}RTFM{RES}!' )
	exit(1)

# def get_status(driver):
# 	try:
# 		driver.execute(Command.STATUS)
# 		return True
# 	except:
# 		return False

def user_pass ( tweet ) :
	return tweet.split(' ')[1] if 'contains credentials' in tweet else None

def tweepyApiInit(conf_file):
	# getting your keys
	config = configparser.ConfigParser()
	config.read( conf_file )

	try:
		consumer_key = config['TWEEPY']['consumer_key']
		consumer_secret = config['TWEEPY']['consumer_secret']
		access_key = config['TWEEPY']['access_key']
		access_secret = config['TWEEPY']['access_secret']
	except Exception as e:
		print( f'[{R}E{RES}] Missing {e} on tweet_API.conf!' )
		exit(1)

	# authorize twitter, initialize tweepy
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	return tweepy.API(auth)

def logError(e):
	ct = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
	with open( ERRORS_FILE , 'a' ) as af :
		print( f'[{R}E{RES}] We got an {R}ERROR{RES}!' )
		af.write( f'---------------- !!Error!! ----------------\nTime and date: {ct}\n{str(e)}\n\n' )

def writeDump(file, text):
	with open( file, 'w+' ) as ff:
		ff.write(text)

##### main
print( f'[{Y}~{RES}] Connecting Tweeter {Y}^.^{RES}' )
api = tweepyApiInit(API_CONF_FILE)
print( f'[{G}+{RES}] Connected {G}:D{RES}' )

## making stuff ready for the looooooop
print( f'[{C}i{RES}] If you get sick looping just press brutally Ctrl+C.' )
nTweets = 200
credz_curr = 0
credz_canc = 0
credz_tot = sum( 1 for line in open( PASTE_FILE ) )
errors = 0
tweet_api_errors = 0

## selenium stuff
profile = webdriver.FirefoxProfile()
profile.set_preference("dom.webdriver.enabled", False)
profile.update_preferences()
desired = DesiredCapabilities.FIREFOX
options = Options()
options.headless = True
if fir_bin:
	driver = webdriver.Firefox(firefox_binary=fir_bin, options=options, firefox_profile=profile, desired_capabilities=desired)
else:
	driver = webdriver.Firefox(options=options, firefox_profile=profile, desired_capabilities=desired)
time.sleep(1)

while True :

	if tweet_api_errors > 10:
		print( f'[{R}E{RES}] Something is not right with your Tweeter API!' )
		exit(1)

	try:
		scav_tweets = api.user_timeline(screen_name = 'leak_scavenger', count = nTweets , include_rts = True)
		tweet_api_errors = 0
	except tweepy.TweepError as e:
		print( f'[{R}E{RES}] Tweepy got stuck!' )
		logError(e)
		errors += 1
		tweet_api_errors += 1
		time.sleep(10)
		scav_tweets = []
		continue

	print( f'[{C}~{RES}] Parsing the hell out of the {R}scavenger!{RES} {C}o.O{RES}' )

	for tweet in scav_tweets :
		userpass_link = user_pass( tweet.text )

		if userpass_link:
			if not userpass_link in l_list:
				
				with open( PASTE_FILE , 'a' ) as af :
					af.write( f'{userpass_link}\n' )
				l_list.append(userpass_link)

				s = requests.Session()
				r = s.get( userpass_link , headers=headers, allow_redirects=True )
				rLink = re.findall( r'(?:;URL=)(.*?)(?:"><)' , r.text )[0]

				temp_filename = f'{DUMP_FOLDER}{hashlib.md5(rLink.encode()).hexdigest()}'

				if 'pastebin' in rLink :
					if r.status_code == 200 or r.status_code == 403 :
						print( f'[{Y}-{RES}] downloading {rLink} {Y}o.O{RES}' )
						dump = s.get( rLink )
						writeDump( temp_filename, dump.text )
						print( f'[{G}+{G}] {G}DOWNLOADED!!{RES} --> {temp_filename}' )
						credz_curr += 1
						credz_tot += 1
					else :
						print( f'[{R}x{RES}] too late!!' )
						credz_canc += 1

				elif 'ghostbin' in rLink:
					print(rLink)
					driver.get( rLink )
					print( f'[{Y}-{RES}] downloading {rLink} {Y}o.O{RES}' )

					ccc = 0
					## wait for Cl0u*f74r3 to think 
					## that my bot is not a bot
					## so that my bot can check 
					## stuff that the bots cannot check
					_ = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
					while 'Checking your browser before accessing' in driver.page_source:
						if ccc > 100:
							print( f'[{R}x{RES}] mmmmh.. did Cl0u*f74r3 got me?' )
							e = f'Got stuck here:\n{driver.page_source}'
							logError(e)
							break
						time.sleep(0.3)
						ccc += 1

					soup = BeautifulSoup(driver.page_source, features='lxml')
					with open( temp_filename, 'w+' ) as ff:
						ff.write(soup.text)

					print( f'[{G}+{RES}] {GG}DOWNLOADED!!{RES} --> {temp_filename}' )
					credz_curr += 1
					credz_tot += 1

				else:
					print( f'[{R}x{RES}] I am sure that "{rLink}" is not a url --> {R}:({RES}' )
					logError(f'Weird link --> {rLink}')

			else :
				print( f'[{R}x{RES}] Nothing new to be exited about --> {R}:({RES}' )
				
	print( f'[{C}i{RES}] Script started @ {C}{STARTED}{RES}!' )
	if errors > 0:
		print( f'[{C}*{RES}] {C}Tweepy{RES} got {R}{errors}{RES} errors!' )
	else:
		print( f'[{Y}-{RES}] {Y}No errors.{R} So far so good {RES}' )
	if credz_canc > 0:
		print( f'[{R}*{RES}] LOST {R}{credz_canc}{RES} paste you SLOW!' )
	else:
		print( f'[{Y}-{RES}] LOST {Y}NO{RES} pastes so far! Keep it up!' )
	print( f'[{G}+{RES}] Downloaded {G}{credz_curr}{RES} paste on thiz sesh {G}:F{RES}' )
	print( f'[{G}+{RES}] Downloaded {GG}{credz_tot}{RES} paste on total {GG}^0^{RES}' )
	print( f'[{C}O{RES}] Sleeping a bit {C}-.-{RES}' )
	time.sleep(60)
	nTweets = 20
