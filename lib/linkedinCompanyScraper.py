#!/usr/bin/env python3.8

from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lib import googleImageSearch
import time
import random

class LinkedIn :
    def __init__( self, log, stash ):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        # self.driver = webdriver.Chrome()

        # self.driver.set_network_conditions( offline=False,
        #                                latency=9,  # additional latency (ms)
        #                                download_throughput=50 * 1024,  # maximal throughput
        #                                upload_throughput=50 * 1024 )  # maximal throughput

        self.log = log
        self.goog = googleImageSearch.GetThem( log )
        self.stash = stash
        # self.t = concurrent.futures.ThreadPoolExecutor(max_workers=100)
        # self.threads = []

    def __sleep_rand( self ):
        time.sleep( random.randrange(1000,2000) * 0.001 )

    def login( self, email, password ):
        self.driver.get("https://www.linkedin.com/login")
        element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        email_elem = self.driver.find_element_by_id("username")
        email_elem.send_keys(email)
        password_elem = self.driver.find_element_by_id("password")
        password_elem.send_keys(password)
        self.driver.find_element_by_tag_name("button").click()

        element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "profile-nav-item")))

    def pleaseReadMe( self , peep_object , name , pic_link ) :
        try:
            prof_link = peep_object.find_element_by_tag_name( 'a' ).get_attribute( 'href' )
            job_title = peep_object.find_element_by_tag_name( 'p' ).text
        except Exception as e:
            self.log.error( e )

        sqlq = 'INSERT INTO employees( comp_link, name, position, prof_link, prof_pic ) VALUES(?, ?, ?, ?, ?)'
        sqlv = ( self.c_link, name, job_title, prof_link, pic_link )
        self.log.findings( f'Found employye {name}, working as {job_title}' )
        self.stash.sql_execcc( sqlq, sqlv )


    def hardToFind( self, job_title, location, pic_lnk ) :
        try:
            # job_title = infos[0].text
            # location = infos[1].text
            self.log.info( f'User info parsed, trying inverse image search...' )
            name, prof_link = self.goog.getThem( pic_lnk, job_title, location )

            if name and prof_link:
                sqlq = 'INSERT INTO potential_employees( comp_link, name, position, prof_link, prof_pic ) VALUES(?, ?, ?, ?, ?)'
                sqlv = ( self.c_link, name, job_title, prof_link, pic_lnk )
                self.log.findings( f'Found potential employe {name}, working as {job_title}' )
                self.stash.sql_execcc( sqlq, sqlv )
            else:
                pic_lnk = pic_lnk if pic_lnk else 'NA'
                sqlq = 'INSERT INTO hidden_employees( comp_link, position, prof_pic ) VALUES(?, ?, ?)'
                sqlv = ( self.c_link, job_title, pic_lnk )
                self.log.info( f'Impossible to find user. Details saved anyway.' )
                self.stash.sql_execcc( sqlq, sqlv )

        except Exception as e:
            self.log.error( e )


    def sortEmployee( self , emp_obj ) :
        #checking if the name is pubblic
        try :
            name = emp_obj.find_element_by_class_name( "actor-name" ).text
        except Exception as e :
            self.log.error( e )

        # checking if there is any pic
        try :
            pic_link = emp_obj.find_element_by_tag_name( 'img' ).get_attribute( 'src' )
        except Exception as e :
            self.log.warning( 'No profile pic' )
            pic_link = None


        if name != 'LinkedIn Member':
            self.pleaseReadMe( emp_obj , name , pic_link )
        else :
            try:
                infos = emp_obj.find_elements_by_tag_name( 'p' )

                if pic_link:
                    self.log.info( f'Need to google this pic --> {pic_link}' )
                    self.hardToFind( infos[0].text, infos[1].text, pic_link )
                    # self.threads.append( self.t.submit( self.hardToFind, infos[0].text, infos[1].text, pic_link ) )
                else:
                    self.log.warning( f'This one is a ghost, manual research needed!' )
                    # self.threads.append( self.t.submit( self.hardToFind, infos[0].text, infos[1].text, None ) )
                    self.hardToFind( infos[0].text, infos[1].text, None )

            except Exception as e:
                self.log.warning( 'No user info' )
                infos = None

    def scrapeThoseEmployeez( self, email, password, company_url ):
        self.c_link = company_url
        self.login( email , password )

        # marks xpath
        currentPage = "//button[@aria-current='true']"
        list_css = "search-results"
        peepz = '//div[@data-test-search-result="PROFILE"]'
        next_xpath = '//button[@aria-label="Next"]'
        chat_xpath = '//header[@data-control-name="overlay.minimize_connection_list_bar"]'
        chat_down_xpath = '//header[@data-control-name="overlay.maximize_connection_list_bar"]'

        employees = []

        self.log.info( f'Scraping the employees from {self.c_link}' )
        self.driver.get( self.c_link )

        self.__sleep_rand()
        self.driver.execute_script( f'window.scrollTo(0, Math.ceil(document.body.scrollHeight/{ 1 / random.random() }));' )

        self.__sleep_rand()
        see_all_employees = self.driver.find_element_by_xpath('//a[@data-control-name="topcard_see_all_employees"]')
        self.driver.get(see_all_employees.get_attribute("href"))


        _ = WebDriverWait(self.driver, 15 ).until(EC.presence_of_element_located((By.CLASS_NAME, list_css)))
        _ = WebDriverWait(self.driver, 20 ).until(EC.presence_of_element_located((By.XPATH, chat_xpath)))

        self.driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight*3/4));")

        self.driver.find_element_by_xpath( '//section[@class="msg-overlay-bubble-header__details flex-row align-items-center"]' ).click()
        # yes I know, do not judge me, this chat is fucking killing me
        while True:
            try:
                _ = WebDriverWait(self.driver, 10 ).until(EC.presence_of_element_located((By.XPATH, chat_down_xpath)))
                time.sleep(1.2)
                break
            except Exception as e:
                self.log.warning('That chat is not going down againt... trying it again...')
                self.driver.find_element_by_xpath( '//section[@class="msg-overlay-bubble-header__details flex-row align-items-center"]' ).click()
                continue

        try:
            totPages = self.driver.find_elements_by_xpath("//li[@class='artdeco-pagination__indicator artdeco-pagination__indicator--number ember-view']")[-1].text
        except Exception as e:
            log.error('I guess linkedin changed the page xpath again --> {e}')
            sys.exit(1)

        self.log.info( f'Total pages found --> {totPages}' )

        for p in range ( int(totPages) ):
            self.driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/4));")
            self.__sleep_rand()
            self.driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/3));")
            self.__sleep_rand()
            self.driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));")
            self.__sleep_rand()
            self.driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight));")
            self.__sleep_rand()

            results_list = self.driver.find_element_by_class_name(list_css)
            # results_li = results_list.find_elements_by_tag_name("li")
            results_li = results_list.find_elements_by_xpath( peepz )

            # self.threads = [ self.t.submit( self.sortEmployee, res) for res in results_li ]
            for res in results_li:
                self.sortEmployee( res )

            pag_num = self.driver.find_element_by_xpath( currentPage )
            p = pag_num.find_element_by_css_selector('span').text
            self.log.info( f'Turning to page {int(p)+1}' )

            self.driver.find_element_by_xpath(next_xpath).click()
            _ = WebDriverWait(self.driver, 10 ).until(EC.presence_of_element_located((By.CLASS_NAME, list_css)))

        self.log.info( f'All pages done!' )
        # self.log.info( f'Waiting all threads to terminate.' )
        # wait = [ x.result() for x in concurrent.futures.as_completed( self.threads ) ]
        self.driver.close()
