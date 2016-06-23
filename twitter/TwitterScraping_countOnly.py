
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import urllib
import calendar
import argparse
import datetime
import random

python_ver = "2"
browser_env = "firefox"
random_interval = True
break_Count = 10

def dformat(date):
    return str(date.year) + "-" + str(date.month) + "-" + str(date.day)

def getCalendar_month(month):
    month_array = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    return month_array[month - 1]

def sformat(date):
    return str(date.day) + " " + getCalendar_month(date.month) + " " + str(date.year)

def extractData(data, tdata, date_source):
    date = datetime.datetime.strptime(date_source,"%Y-%m-%d")
    until = date + datetime.timedelta(days=1)
    r = ["date:data"]
    
    for (e1, e2) in zip(data, tdata):
        tmp = e2.find_all("span")
        t = tmp[0]
        tmp2 = datetime.datetime.fromtimestamp(int(t['data-time']))
        
        if tmp2 > date and until > tmp2:
            r.append("1")
    return r

def writeData(data, tdata, word, date_source):
    #try:
        date = datetime.datetime.strptime(date_source,"%Y-%m-%d")
        f = open("output_countonly_"+ word + "_" + date_source +".txt","w")
        r = extractData(data, tdata, date_source)
        #for e in r:
            #print(e + "\n")
            #f.write(e + "\n")
        #f.close()
        f.write(str(len(r)))
        f.close()
        print("Finish word: " + word +" date:" + date_source)
    #except:
        #print("save error!")

def Ichiyo(word, since, until , interval):
    since = datetime.datetime.strptime(since,"%Y-%m-%d")
    until = datetime.datetime.strptime(until,"%Y-%m-%d")
    date = since
    while ((date - until) != datetime.timedelta(days=0)):
        date_source = dformat(date)
        r = TWscraping(word, date_source, interval)
        writeData(r[0], r[1], word, date_source)
        date = date + datetime.timedelta(days=1)


def TWscraping(word, date_source, interval):
    check = 0
    date = datetime.datetime.strptime(date_source,"%Y-%m-%d")
    if python_ver == "3":
        url = urllib.parse.quote(str(word) + " since:" + dformat(date - datetime.timedelta(days=1)) + " until:" + dformat(date + datetime.timedelta(days=1)))
    else:
        url = urllib.quote(str(word) + " since:" + dformat(date - datetime.timedelta(days=1)) + " until:" + dformat(date + datetime.timedelta(days=1)))
    
    if browser_env == "chrome" or browser_env == "Chrome":
        browser = webdriver.Chrome("./chromedriver")
    else:
        browser = webdriver.Firefox()
    browser.get("https://twitter.com/search?q=" + url)
    
    count = 0;
    counttemp = 1;
    print("Getting... word: " + word +" date:" + date_source)
    
    try:
        while(check < break_Count):
            if(count == counttemp):
                check = check + 1
                print("check:" + str(check) + "/" + str(break_Count))
            count = counttemp
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            if(random_interval):
                interval = random.uniform(1,5)
            time.sleep(interval)
            html = browser.page_source.encode('utf-8')
            counttemp = len(html)
    except:
        print("Error!!")
    
    soup = BeautifulSoup(html, "lxml")
    result = soup.find_all("p", class_="TweetTextSize js-tweet-text tweet-text")
    result1 = soup.find_all("a",class_="tweet-timestamp js-permalink js-nav js-tooltip")
    browser.quit()
    return [result, result1]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search and Scraping Twitter Data!")
    parser.add_argument("word", help=u"Search key word")
    parser.add_argument("since", help=u"get twitter data since this date. example: 2016-04-03")
    parser.add_argument("until", help=u"get twitter data until this date. example: 2016-04-04")
    parser.add_argument("-d", dest="date",help="example: 2015-8-12")
    parser.add_argument("-i", dest="interval", default=1000, help=u"Update interval: Short if it fails do not cry.")
    parser.add_argument("-p", dest="pyversion", default=2, help="python version default 2")
    parser.add_argument("-b", dest="browser",default="firefox",help="if you will use Chrome [-b Chrome] or [-b chrome]")
    args = parser.parse_args()
    
    python_ver = args.pyversion
    browser_env = args.browser
    
    if(args.interval != 1000):
        random_interval = False    
    
    #TWscraping(args.word, args.date, args.interval)
    Ichiyo(args.word, args.since, args.until, int(args.interval))
    

