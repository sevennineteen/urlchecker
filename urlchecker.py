import argparse
import codecs
import httplib2
import urllib
import lxml.html
from datetime import datetime
import string
import random

parser = argparse.ArgumentParser()
parser.add_argument('--urls', help="Path to file including URLs to check")
parser.add_argument('--root', help="Root URL to prepend to URLs")
parser.add_argument('--report', help="File for report output")
#parser.add_argument('--certs', help="Perform SSL certificate validation")
args = parser.parse_args()

#----------------------------------------------------------------------------------
# Project-specific constants
URL_LIST_PATH = args.urls or 'urls.txt'
SITE_ROOT = '' if args.root == 'ABSOLUTE' else args.root or 'http://www.yoursite.com'
REPORT = codecs.open(args.report or 'report-%s.txt' % (datetime.now().strftime('%m%d%y')), 'w', 'utf-8')
#----------------------------------------------------------------------------------

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    "Generate random string (to randomize User-Agent and avoid being throttled)."
    return ''.join(random.choice(chars) for x in range(size))

def report(msg):
    "Prints message to console and write to report file."
    try:
        print msg
        REPORT.write('%s\n' % msg)
    except UnicodeEncodeError, err:
        # Delete rightmost column until successful
        msg_list = msg.split('\t')
        msg_list.pop()
        return report('\t'.join(msg_list))

def get_page_title(content):
    "Gets contents of HTML title tag."
    t = lxml.html.document_fromstring(content)
    return t.find(".//title").text.strip()

def check_url(url, prefix=''):
    "Sends GET request to url and records response data."
    
    test_result = []
    redirect_target = None
    
    try:
        test_result.append(prefix + url)
        
        http = httplib2.Http(timeout=10, disable_ssl_certificate_validation=True)
        http.follow_redirects = False
        response, content = http.request(url, headers={'User-Agent': 'Python-urllib 3.1-%s' % RANDOM_STRING})
        
        test_result.append(response.status)
        
        # Get title for found pages
        if response.status in [200, 404] and 'text/html' in response['content-type']:
            test_result.append(get_page_title(content))
        
        # Get target for redirects
        if response.status in range(301, 304):
            redirect_target = response['location']
            test_result.append(redirect_target)
        
    except Exception, e:
        test_result.append(e)
    
    report('\t'.join(['%s' % x for x in test_result]))
    
    # For redirects, check target URL
    if redirect_target:
        return check_url(redirect_target, '>> ')

RANDOM_STRING = id_generator()

report('\t'.join(['URL', 'STATUS CODE', 'TITLE/LOCATION']))

f = open(URL_LIST_PATH, 'r')
for url in [x for x in f.readlines() if x[0] != '#']:
    check_url(SITE_ROOT + urllib.quote(url.strip()))
f.close()

REPORT.close()