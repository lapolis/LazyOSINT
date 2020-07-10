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

### Installing python-pip for python 3.8 and Libreoffice
```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python3.8 get-pip.py
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
cd LazyOSINT/
pip3.8 install -r requirements.txt
chmod +x ./main.py
./main -h
```


# Usage Examples
#### Run a full domain enumeration targeting "londonmet.ac.uk", save the database "myDatabaseName" and the log file "myLogFile".
```
./main.py -f myDatabaseName -d londonmet.ac.uk -l myLogFile
```

#### Run the LinkedIn scraping module against LondonMet LinkedIn page using as a ALREADY EXISTING LinkedIn account email "example@gmail.com" with password "password" and save all the data database "myDatabaseName".
If you do not specify the LinkedIn password in the command line it will be asked later.
```
./main.py -f myDatabaseName -u https://www.linkedin.com/school/london-metropolitan-university/ -e example@gmail.com -p password
```

#### Run the LinkedIn scraping module and a full domain enumeration.
```
./main.py -f myDatabaseName -u https://www.linkedin.com/school/london-metropolitan-university/ -e example@gmail.com -d londonmet.ac.uk -l myLogFile
```


# TODO
Potential TODO list to complete if I ever survive to OSCP:
- Add more checks on the LinkedIn module
- check if password was the right one in selenium
- find more than 1k employees (LinkedIn limit to 100 pages)
- use proxy for google - not working, still reCAPTCHA
- Generate a potential email based on a company template
