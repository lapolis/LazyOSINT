# LazyOSINT
Yet another multithreading OSINT automator.

<p align="center">
  <img src="https://github.com/lapolis/LazyOSINT/blob/master/LazyOSINT_small.png?raw=true">
</p>


# Intro

LazyOSINT born from a simple Bash script I made to automate the initial enumeration during my internship last summer. The decision to switch to Python and improve it came last October when I had to decide what to develop as my final year project.

LazyOSINT uses sublist3r by aboul3la in order to passively gather all the subdomains available from all the sources listed in sublist3r. Then it resolves all the subdomains and query Shodan to enumerate potential open ports and the respective headers.

While that enumeration runs, using Selenium, it retrieves all the employees from the company’s LinkedIn account. In case of a private user, a quick google search is done trying to reveal the real name behind that hidden profile. Unfortunately, the queries to Google are limited but all the intelligences are saved and the research can be manually carried out.

All the data is written in a SQLite database.

I am aware of the fact that it might be a bit messy, open to suggestions by whoever feels like giving some tips.

A huge “thank you” goes to Fausto Fasan for the magnificent logo! --> [LinkedIn](https://www.linkedin.com/in/fausto-fasan-4587a71a9/)

# Installation

To use Shodan please put the API key in the file `API_KEYS.conf` .

### Installing python-pip for python 3.8 and SOX (for the beep)
```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python3.8 get-pip.py
sudo apt install sox
```

### Installing Sublist3r
```
git clone https://github.com/aboul3la/Sublist3r.git
cd Sublist3r/
sudo python3.8 setup.py install
cd ..
```

### Installing LazyOSINT
```
git clone https://github.com/lapolis/LazyOSINT.git
cd LazyOSINT/
pip3.8 install -r requirements.txt
chmod +x ./main.py
./main.py -h
```


# Usage Examples
<b>Run the LinkedIn scraping module AND a full domain enumeration.</b>
```
./main.py -f myDatabaseName -u https://www.linkedin.com/school/london-metropolitan-university/ -e example@gmail.com -d londonmet.ac.uk -l myLogFile
```

<b>Run a full domain enumeration</b> targeting "londonmet.ac.uk", save the database "myDatabaseName" and the log file "myLogFile".
```
./main.py -f myDatabaseName -d londonmet.ac.uk -l myLogFile
```
## LinkedIn stuff
If you do not want to submit your LinkedIn email and password as a argument, just omit `-e` and `-p`, LazyOSINT will ask both when needed.

<b>Run the LinkedIn scraping module</b> against LondonMet LinkedIn page using as a ALREADY EXISTING LinkedIn account email "`example@gmail.com`" with password "password" and save all the data database "myDatabaseName".
If you do not specify the LinkedIn password in the command line it will be asked later.
```
./main.py -f myDatabaseName -u https://www.linkedin.com/school/london-metropolitan-university/ -e example@gmail.com -p password
```

<b>Resume</b> the LinkedIn scraping module against LondonMet page that has been interrupted (also after reboot). Please note that the url MUST be the same string ( `https://www.linkedin.com/school/london` != `https://www.linkedin.com/school/london/` ).
```
./main.py -f myDatabaseName -u https://www.linkedin.com/school/london-metropolitan-university/ -r
```

<b>Stop at reCaptcha</b>. This was a request I got which actually make sense. If you have a nice VPN you might be able to change IP and then carry on with the scan.
Every time it stops, you are asked whether you want to retry the same query where you got the reCaptcha or if you want to pass and go to the next one. Please <b>note</b> that if you are running the domain enumeration, that message will likely go out of screen; at this point you can either input the answer `[Yy/Nn]` or press enter and get the question printed again.
```
./main.py -f myDatabaseName -u https://www.linkedin.com/school/london-metropolitan-university/ -b
```

<b>Stop at reCaptcha</b> and <b>BEEEP!</b>. Yes, it will make a sound whenever a reCaptcha is hit. (I might add more ringtone in the future lol). (You need to install `sox`)
```
./main.py -f myDatabaseName -u https://www.linkedin.com/school/london-metropolitan-university/ -B
```

<b>Skip Google dorking</b>. This is just in case you have tons of contacts and you prefer to be quick rather than trying to find all the hidden users. The private users information are stored anyway.
```
./main.py -f myDatabaseName -u https://www.linkedin.com/school/london-metropolitan-university/ -S
```

# Full helper
```
usage: main.py [-h] [-f DB_FILE] [-s] [-d DOMAIN] [-l LOG_FILE] [-e EMAIL] [-p PASSWORD] [-u LINKEDIN_URL] [-N] [-B] [-b] [-S] [-r] [-v]

This is the the full list of availables flags for LazyOSINT v0.2.

optional arguments:
  -h, --help                        Show this help message and exit
  -f DB_FILE, --db_file DB_FILE     Name of the sqlite database used to store any retreived information.
  -s, --sneaky                      Do not show any LOG on screen.
  -d DOMAIN, --domain DOMAIN        Target domain.
  -l LOG_FILE, --log_file LOG_FILE  Name of file where to write all the logs.
  -e EMAIL, --email EMAIL           Linkedin registered email address.
  -p PASSWORD, --password PASSWORD  Linkedin password. If omitted and arg -u is given, you will be prompted fro a password.
  -u LINKEDIN_URL, --linkedin_url LINKEDIN_URL
                                    Target company's Linkedin Profile. Example --> https://www.linkedin.com/company/niceCompanyName/
  -N, --no_resolv                   Do NOT resolv subdomains nor check for open ports.
  -B, --beeep_n_pause_captcha       Pause when LazyOSINT hits reCAPTCHA and Beep!
  -b, --pause_captcha               Pause when LazyOSINT hits reCAPTCHA, no beep.
  -S, --skip_google                 Skip Google search for hidden profiles.
  -r, --resume_linkedin             Resume an interrupted LinkedIn scraper - Need to specify the exact same LinkedIn url (-u).
  -v, --version                     Just print version and exit.
```


# TODO
Potential TODO list to complete if I ever survive to OSCP:
- Add more checks on the LinkedIn module
- check if password was the right one in selenium
- find more than 1k employees (LinkedIn limit to 100 pages)
- use proxy for google - not working, still reCAPTCHA
- Generate a potential email based on a company template
