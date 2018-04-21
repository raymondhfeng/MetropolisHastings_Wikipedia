import re
import os
import sys
import urllib
import urlparse
import random
import requests
import json
import wikipedia
import numpy as np
from bs4 import BeautifulSoup



# ---- helper functions -----

def help_total_est(urlx, num_samples = 20):

    try:
        curr_page = wikipedia.page(urlx)
    except:
        return -2

    num_links = len(curr_page.links)

    errors = 0
    sumVal = 0
    curr_iter = 0
    samples = random.sample(curr_page.links, min(num_samples,num_links))

    for link in samples:

        link = link.replace(" ", "_")
        api_url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/"
        api_url += link
        api_url += "/daily/20151010/20151012"

        try:
            response = requests.get(api_url)
            json_data = json.loads(response.text)
            views = json_data['items'][0]['views']
            # print(link, ": ", views)
            curr_iter += 1
            sumVal += views 

        except:
            errors += 1

    #print("errors: ", errors)
    samp_mean = sumVal / (num_samples - errors)
    #print("sample mean: ", samp_mean)
    
    total_est = samp_mean * num_links
    return total_est


def getViews(link):
    link = link.replace(" ", "_")
    api_url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/"
    api_url += link
    api_url += "/daily/20151010/20151012"
    try:
        response = requests.get(api_url)
        json_data = json.loads(response.text)
        views = json_data['items'][0]['views']
        # print(link, ": ", views)
        return views
    except:
        print "link not found when calculating views: ", link
        return -2



# ---- read univ list, create dict -----

def readFile(filename):
    filehandle = open(filename)
    print filehandle.read()
    filehandle.close()

fileDir = os.path.dirname(os.path.realpath('__file__'))
filename = os.path.join(fileDir, 'records/universities.txt')
readFile(filename)
with open(filename) as f:
    content = f.readlines()

content = [x.strip() for x in content] 
profs = content
bad_urls = []

# ---- Creating a dictionary to keep track of how often we come across a university ----
profdict = {}
for i in profs:
    profdict[i] = 0



# ---- initializations -----

#url_start = 'Elon_Musk'
url_start = 'Forbes_Celebrity_100'
current_url = url_start
num_of_visits = 2000
num_samples = 20



# ---- MC Random Walk -----

nonect = 0

for i in range(num_of_visits):

    if nonect > 4:
        current_url = url_start    
        nonect = 0

    print  i , ' Visiting... ', current_url
    url_ini = current_url   

    try:
        curr_page = wikipedia.page(current_url)
    except:
        current_url = url_start
        continue

    url_list = curr_page.links
    len_list = len(url_list)
    print "num_links of url_ini: ", len(url_list)
    view_ini = getViews(url_ini)
    totalest_ini = help_total_est(url_ini)



    # ---- follow a link ----
    if random.random() < 0.9 and len_list > 100:


        # ---- choose next page to visit from url_list ----
        updated = False   
        
        ku = 0
        while not updated and ku < 5:
            ku += 1


            # ---- randomly choose one from url_list ----
            current_url = random.choice(url_list)
            print 'chosen', current_url
            view1 = getViews(current_url)
            total_v1 = help_total_est(current_url)

            if view1 != -2 & total_v1 != -2:

                f_nom = (view_ini) / float(total_v1)

                f_denom = (view1) / float(totalest_ini)

                # OPTION 1
                # score = f_nom / f_denom

                # OPTION 2
                score = totalest_ini / float(total_v1)

                # ---- decide whether or not to visit with acceptance score ----
                if random.random() < min(score , 1):
                    updated = True

        # ---- update univ dict count ----
        print 'visiting', current_url
        text = curr_page.content
        list_of_words = text.split()


        pct = 0
        for p in profs:
            if " " + p + " " in text:
                profdict[p]+=1
                pct += 1
            
        if pct == 0:
            print "NONE FOUND"
            nonect += 1
        else:
            print 'HIT, HAS UNIVERSITY'
    
    else:
        print 'length of list', len_list
        current_url = url_start
        


# ---- return sorted result ----

prof_ranks = [pair[0] for pair in sorted(profdict.items(), key = lambda item: item[1], reverse=True)]
top_score = profdict[prof_ranks[0]] + 1
total = sum([profdict[prof] for prof in profdict]) + 1 #divide by zero

for i in range(len(prof_ranks)):
    print "%d %f: %s" % (i+1,profdict[prof_ranks[i]]/float(top_score), prof_ranks[i])

print('--------------------------------------------')

for i in range(len(prof_ranks)):
    print "%d %f: %s" % (i+1,profdict[prof_ranks[i]]/float(total), prof_ranks[i])

print profdict









        
