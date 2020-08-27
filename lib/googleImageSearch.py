#!/usr/bin/env python3.8

import io
import os
import re
import sys
import time
import random
import hashlib
import requests
from PIL import Image
from urllib.parse import quote
import requests_random_user_agent

class GetThem:
    def __init__( self, log, pause, b_pause ):
        self.log = log
        self.gooBan = True

        self.pic_dir = os.path.join( os.path.abspath( sys.argv[0].replace( 'main.py' , '' ) ), 'out', '.temp_pic' )
        self.ghost_pic = os.path.join( os.path.abspath( sys.argv[0].replace( 'main.py' , '' ) ), 'lib', 'ghost.png' )
        if not os.path.isdir( self.pic_dir ):
            os.makedirs( self.pic_dir )

        self.pause = pause
        self.b_pause = b_pause

    def download_img( self, url ):
        self.log.info( f'Trying to download {url}' )
        try:
            image_content = requests.get(url).content
        except Exception as e:
            self.log.error( f'Could not download {url} - {e}' )

        try:
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert('RGB')
            file_path = os.path.join( self.pic_dir, hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
            with open(file_path, 'wb') as f:
                image.save(f, "JPEG", quality=95)
                self.log.findings( f'SUCCESS - saved {url} - as {file_path}' )

            return file_path

        except Exception as e:
            self.log.error( f'ERROR - Could not save {url} - {e}' )

    def waitRand( self ):
        ttt = random.randint(1000000000,6000000000)/10000000000
        self.log.info( f'Sleeping --> {ttt} seconds' )
        time.sleep( ttt )

    def getThem( self, img_link, job_title, location ):

        name = None

        if self.gooBan:
            s = requests.Session()
            self.job_title = quote( job_title )
            self.location = quote( location )

            if img_link:
                img_path = self.download_img( img_link )
            else :
                img_path = self.ghost_pic

            self.waitRand()
            self.log.info( f'Generating the google query.' )
            searchUrl = 'http://www.google.co.uk/searchbyimage/upload'
            multipart = {'encoded_image': (img_path, open(img_path, 'rb')), 'image_content': ''}
            response = s.post(searchUrl, files=multipart, allow_redirects=False )
            fetchUrl = response.headers['Location']
            refined_url = fetchUrl + f'&q=site%3Alinkedin.com+%22{self.job_title}%22+%22{self.location}%22&oq=site%3Alinkedin.com+{self.job_title}+{self.location}'

            self.waitRand()
            search_results = s.get( refined_url )

            self.log.info( f'Analysing Google response.' )
            ###########################################
            # # reg = r'<h3 class=\".{7}>(.*?)</h3>'
            # reg = r'<h3 class=\".{7}>(.*?)</h3>'
            # reg = r'<h3 class=\".{7}>(.*?)</h3>'
            # regPlus = r'\">[1-9][0-9]\+(.*?)</h3'
            # temp_name = f'/tmp/{time.time()}.html'
            # with open( temp_name , 'w' ) as xx:
            #     xx.write( search_results.text )
            ###########################################

            reg = r'<h3 class=\".{7}>(.*?)</h3>'
            regPlus = r'\">[1-9][0-9]\+(.*?)<\/h3'
            BAN = 'Our systems have detected unusual traffic from your computer network'
            linkIN = r'<a href\=\"(https:\/\/uk\.linkedin\.com\/in\/.*?)\"'
            size = '200 - '
            nothing = 'did not match any documents.'

            # findings = re.findall( regPlus , search_results.text )

            general = re.findall( linkIN , search_results.text )
            link = general[0] if general else None

            if link:
                name = ' '.join( link.split( '/' )[-1].split('-')[:-1] )
                self.log.findings( f'Found potential matching account --> {name}' )
            elif BAN in search_results.text:
                self.log.error( 'GOOGLE threw a reCAPTCHA.' )
                if self.pause or self.b_pause:
                    return None, None, True

                else:
                    self.gooBan = False

            elif nothing in search_results.text:
                self.log.warning( 'No results for this query.' )

            if img_path != self.ghost_pic :
                self.log.info( f'Deleting the picture.' )
                os.remove( img_path )

        else:
            self.log.error( '''Google doesn't like us anymore''' )

        if name and link:
            return name, link, False
        else:
            return None, None, False
