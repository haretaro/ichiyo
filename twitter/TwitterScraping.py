
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import urllib
import calendar
import argparse
import datetime

def dformat(date):
    return str(date.year) + "-" + str(date.month) + "-" + str(date.day)

def sformat(date):
    return str(date.day) + " " + calendar.month_abbr[date.month] + " " + str(date.year)

def extractData(data, tdata, date_source):
    date = datetime.datetime.strptime(date_source,"%Y-%m-%d")
    r = ["date:data"]
    
    for (e1, e2) in zip(data, tdata):
        if sformat(date) == e2.text:
            r.append(date_source + " :" + e1.text.replace("\n", " ").encode('utf-8'))
    return r

def writeData(data, tdata, word, date_source):
    #try:
        date = datetime.datetime.strptime(date_source,"%Y-%m-%d")
        f = open("output_"+ word + "_" + date_source +".txt","w")
        r = extractData(data, tdata, date_source)
        for e in r:
            f.write(e + "\n")
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
    date = datetime.datetime.strptime(date_source,"%Y-%m-%d")
    url = urllib.quote(str(word) + " since:" + dformat(date - datetime.timedelta(days=1)) + " until:" + dformat(date + datetime.timedelta(days=2)))
    browser = webdriver.Firefox()
    browser.get("https://twitter.com/search?q=" + url)
    
    count = 0;
    counttemp = 1;
    print("Getting... word: " + word +" date:" + date_source)
    
    try:
        while(count < counttemp):
            count = counttemp
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(interval)
            html = browser.page_source.encode('utf-8')
            soup = BeautifulSoup(html, "lxml")
            result = soup.find_all("p", class_="TweetTextSize js-tweet-text tweet-text")
            result1 = soup.find_all("a",class_="tweet-timestamp js-permalink js-nav js-tooltip")
            counttemp = len(result)
            print("Twitte count : " + str(count))
    except:
        print("Error!!")
    browser.quit()
    return [result, result1]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search and Scraping Twitter Data!")
    parser.add_argument("word", help=u"Search key word")
    parser.add_argument("since", help=u"")
    parser.add_argument("until", help=u"")
    parser.add_argument("-d", dest="date",help="example: 2015-8-12")
    parser.add_argument("-i", dest="interval", default=2, help=u"Update interval: Short if it fails do not cry.")
    args = parser.parse_args()
    
    #TWscraping(args.word, args.date, args.interval)
    Ichiyo(args.word, args.since, args.until, args.interval)
    

