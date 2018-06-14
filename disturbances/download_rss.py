#!/usr/bin/env python2.7

# Download all files from given RSS into one file
# Quick fix and hack on https://gist.github.com/kmonsoor/10727871

"""
Parallel RSS-Feed Downloader
----------------------------
    Download contents by grabbing links from a given RSS-feed.
    Works over HTTP,FTP,HTTPS protocol transparently.
    Currently, works on Linux, Mac OSX, and possibly on other Unix as well. 
               But, _NOT_ on Windows * yet.
__project__ = "Parallel RSS-Feed Downloader"
__author__  = "Khaled Monsoor <k@kmonsoor.com>"
__license__ = "MIT"
__version__ = "1.0"
__python__  = "2.7.*"
Usage: 
------
    python parallel_rss_download.py  --feed=<feed_url>
    
Pre-requisites:
---------------
  *  OS: Linux / Mac OS / Unix  (Windows' support NOT implemented)
  *  Python version: 2.7.0 +
  *  Required Modules:
        * URLGrabber < http://urlgrabber.baseurl.org >
            - Installation: "sudo pip install urlgrabber"
        * PycURL < http://pycurl.sourceforge.net/ >
            - Installation: "sudo apt-get install python-pycurl"
Features:
---------
  *  Transparency over protocols like HTTP, HTTPS, or FTP
  *  Multi-threaded simultaneous downloading
  *  Completion of previous partial-downloads
  *  skip previously completed downloads
  *  Automatic retry mechanism
  *  Exception handling
  *  Proxy support
TODO
----
  *  Update logging mechanism to have logging to file
  *  Implement progress meter using URLGrabber's hook
  *  Custom download location
  *  Checking file's timestamp and checksum \
            for checking the completion of a download
  *  Utilize callback hook
  *  Implement nicely handling KeyboadInterruptError,
            caused by user's CTRL+C
  *  smarter feed parsing
  
"""


from urlgrabber.grabber import URLGrabber, URLGrabError
import xml.etree.ElementTree as xmlparse
import multiprocessing as mp
import datetime as dt
import urllib2 as u2
import signal
import argparse
import sys
import os
import time


# ===============================
# Default Download configurations
# ===============================
default_proxy   = None
default_timeout = 300
default_retry   = 3
thread_count    = 5
# ===============================

# Not utilized yet
def init_worker():
    # registering CTRL+C as UserInterrupt
    signal.signal(signal.SIGINT, signal.SIG_IGN) 


def threaded_download(single_download, logfile=None):
    """
    This method initiate with an URL as a thread from a threadPool.
    But on its own, it is not thread-safe. It has to be managed to the caller
    
    Download location: <Current Directory>
    single_download --> complete download link
    logfile         --> use default logfile if not supplied with.
    """
    # registering CTRL+C as UserInterrupt
    # signal.signal(signal.SIGINT, signal.SIG_IGN) 
    
    response = "Not Downloaded"
    try:
        download_size = int((u2.urlopen(single_download)).info().getheaders("Content-Length")[0])   
        print "Starting: "+ str(single_download) + " :: Download target's size: %s KB" % (download_size/1024)
        
        g = URLGrabber(reget='simple', retry=default_retry, timeout=default_timeout, proxies=default_proxy)
        
        response = g.urlgrab(single_download)
        print "Completed: "+ response

    except URLGrabError as ue:
        print str(ue) + "\nskipping: " + single_download
    else:
        return response # response --> downloaded file's name, if download is successful



def download(feed_url):

    try:
        tree = xmlparse.parse(u2.urlopen(feed_url))
    except u2.URLError:
        print "ERRor: URL Not forund"
    except u2.ValueError:
        print "ERRor: Invalid URL" 
    except ParseError:
        print "ERRor: Invalid Feed"

    # it checks RSS' validity
    if str(tree.getroot()).find("rss") > 0:
        # parsing the feed for the download links
        all_downloads = [item.findtext('link') for item in tree.iterfind('channel/item')]
    else:
        print "Sorry : The given URL is not a valid RSS feed."
        exit(0)

    

    print "Feed URL grabbed and parsed successfully \
                        List of targeted downloads\n \
                        --------------------------"
    
    outfilename = "dist_cache/"+dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".log"
    outfile = open(outfilename,"wb")
    for x in all_downloads: 
        print x
        response = u2.urlopen(x)
        outfile.write(response.read())
        
    outfile.close()
        

    
if __name__ == '__main__':
    cli = argparse.ArgumentParser(description='Download contents by grabbing links from a given RSS-feed')
    cli.add_argument('--feed', dest='feed_url', action='store', help='URL of the RSS feed')
    #cli.add_argument('--output', dest='local_location', action='store', help='local folder, where to save the files')
    
    parsed_arguments = cli.parse_args(sys.argv[1:])
    
    if parsed_arguments.feed_url==None:
        print "Error: Sorry. Feed-URL cannot be empty. Quitting from requested job ..."
        exit(0)
    else:
        feed_url = parsed_arguments.feed_url
    
while True:
    download(feed_url)
    time.sleep(10)
