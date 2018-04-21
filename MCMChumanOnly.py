import re
import os
import sys
import urllib
import urlparse
import random
import requests
import json
from bs4 import BeautifulSoup
people_visited = []

class MyOpener(urllib.FancyURLopener):
   version = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15'

def domain(url):
    """
    Parse a url to give you the domain.
    """
    # urlparse breaks down the url passed it, and you split the hostname up 
    # ex: hostname="www.google.com" becomes ['www', 'google', 'com']
    hostname = urlparse.urlparse(url).hostname.split(".")
    hostname = ".".join(len(hostname[-2]) < 4 and hostname[-3:] or hostname[-2:])
    return hostname

bad_keywords = ['#', 'Category:', 'Special:', 'Portal:', 'File:', '.jpg', 'oldid', 'mobileaction=', \
    'printable=', 'action=', 'Wikipedia:', 'Help:', 'User:', 'Talk:', 'Wikipedia:', 'Geographic_coordinate_system', \
    'List_of_sovereign_states', 'Urban_area', 'Eastern_European_Time', 'UTC%2B', 'Daylight_saving_time',  
    ]    

def parse_links(url, url_start):
    """
    Return all the URLs on a page and return the start URL if there is an error or no URLS.
    """
    url_list = []
    myopener = MyOpener()
    try:
        # open, read, and parse the text using beautiful soup
        page = myopener.open(url)
        text = page.read()
        page.close()
        soup = BeautifulSoup(text, "html")

        # find all hyperlinks using beautiful soup
        for tag in soup.findAll('a', href=True):
            # concatenate the base url with the path from the hyperlink
            tmp = urlparse.urljoin(url, tag['href'])
            # we want to stay in the berkeley EECS domain (more relevant later)...
            #if domain(tmp).endswith('wikipedia.org') and 'eecs' in tmp:
            #print ('tmp',tmp)
            proc = urlparse.urlparse(tmp).hostname.split(".")
            proc2 = urlparse.urlparse(tmp)

            if domain(tmp).endswith('wikipedia.org') and (proc[0] == 'en'):
                valid = True
                for bad_keyword in bad_keywords:
                    if bad_keyword in tmp:
                        valid = False
                        break
                if valid: 
                    url_list.append((tmp, proc2.path))
        if len(url_list) == 0:
            return [url_start]
        return url_list
    except:
        return [url_start]

url_start = 'https://en.wikipedia.org/wiki/List_of_covers_of_Time_magazine_(2010s)'
current_url = url_start
num_of_visits = 2000 #1500

#List of professors obtained from the EECS page
def readFile(filename):
    filehandle = open(filename)
    print filehandle.read()
    filehandle.close()
fileDir = os.path.dirname(os.path.realpath('__file__'))
filename = os.path.join(fileDir, 'records/universities_usnews50.txt')
readFile(filename)
with open(filename) as f:
    content = f.readlines()
content = [x.strip() for x in content] 
profs = content
bad_urls = ['https://en.wikipedia.org/wiki/Main_Page']

#Creating a dictionary to keep track of how often we come across a professor
profdict = {}
for i in profs:
    profdict[i] = 0


f = open("univ_list.txt", 'w+')
f.write("this is a test\n")

#for i in range(num_of_visits):   
for i in range(num_of_visits):
    text = None 
    print  i , ' Visiting... ', current_url
    mother_url = current_url
    
    if random.random() < 0.97: #follow a link!
        url_list = parse_links(current_url, url_start)
        # print url_list
        # for url in url_list:
        #     api_url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/University_of_California,_Berkeley/daily/20151010/20151012"
        #     response = requests.get(url[0])
        #     # json_data = json.loads(response.text)
        #     # print(json_data['items'][0]['views'])
        
        updated = False
        

        random.shuffle(url_list)
        for i in range(min(100, len(url_list))):
            

            # print("iteration", i)
            current_url = url_list[i][0]


            print(current_url)
            if current_url in bad_urls or current_url == mother_url or "iris" in current_url or "Deptonly" in current_url or "anchor" in current_url or "erso" in current_url: #dealing with more pathologies:
                continue
            myopener = MyOpener()
            try:
                page = myopener.open(current_url)
            except:
                continue
            text = page.read()
            # print(text)
            page.close()
            if "infobox biography" in text:
                people_visited.append(current_url.split('/')[-1])
                updated = True
                #Figuring out which professor is mentioned on a page.
                pct = 0

                list_of_words = text.split()
                positions = [i for i, x in enumerate(list_of_words) if x == "University"]
                for pos in positions:
                    f.write(str(list_of_words[pos - 3:pos + 3])+"\r\n")

                for p in profs:
                    if " " + p + " " in text:
                        profdict[p]+=1
                        pct += 1
                    
                if pct == 0:
                    print ("NONE FOUND")
                    # current_url = url_start
                else:
                    print 'HIT, HAS UNIVERSITY'
                break
        if not updated:
            current_url = url_start


            
    else: 
        #click the "home" button!
        current_url = url_start

f.close()
        
prof_ranks = [pair[0] for pair in sorted(profdict.items(), key = lambda item: item[1], reverse=True)]
top_score = profdict[prof_ranks[0]]
total = sum([profdict[prof] for prof in profdict]) + 1 #divide by zero
for i in range(len(prof_ranks)):
    print "%d %f: %s" % (i+1,profdict[prof_ranks[i]]/float(top_score), prof_ranks[i])
print('--------------------------------------------')
for i in range(len(prof_ranks)):
    print "%d %f: %s" % (i+1,profdict[prof_ranks[i]]/float(total), prof_ranks[i])
print profdict
print(people_visited)