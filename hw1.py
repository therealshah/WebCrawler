from py_bing_search import PyBingSearch
import urllib
import os
from bs4 import BeautifulSoup
import Queue
import lxml
import re
import heapq
from urlparse import urlparse,urljoin
import unicodedata
import sys
from urllib import FancyURLopener
import random
import datetime


initialUrls = [] # hold the initial urls
UrlQueue = Queue.Queue()# hold all the urls in a given pages ( used as a queue)
myHeap =Queue.PriorityQueue()
query = ''
pages = 0
badUrlExtentions = ['.jpg','.jpeg']
encounteredUrls = {}
pagesToBeCrawled = 0 # user inputs how many pages to crawl
fp = open("/home/shah/Downloads/results/output1.txt",'wb') # file used to write the pages we crawled
blackListUrls = ['http://www.amazon.com/','http://www.ebay.com','http://www.youtube.com'] # store all the blacklisted urls we will encounter
 # Will select a random agent from the list
user_agents = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9'
]

class MyOpener(FancyURLopener,object):
	version = random.choice (user_agents)

	# si that when we encounter this error, well do nothing
	def http_error_401(self, url, fp, errcode, errmsg, headers, data=None):
		print '401 error. Doing nothing'
		global fb
		fp.write('Crawling '+ url +', Score: Time: ' + str(datetime.datetime.now()) + ', Code: ', + str(errcode)+ '\n')
		return None	# do nothing
	def http_error_default(self, url, fp, errcode, errmsg, headers, data=None):
		print errcode,'error. Do nothing'
		global fb
		fp.write('Crawling ' + url + ', Score: Time: ' + str(datetime.datetime.now()) + ', Code: ' + str(errcode) + '\n')
		return None



class Node(object): # used to create a page link with the score and all the pages it points to
	def __init__(self,score,url):
		self.score = score # compute the score
		self.name = url # my url
		self.array = [] # store all the urls this page has


	def appendUrl(self,url):# adds the url to array member variable
		self.array.append(url)

	def __cmp__(self,other):
		return self.score<other.score



# get the intial url list
def getTopTen():
	global query
	global pagesToBeCrawled
	global fb
	bing = PyBingSearch('mMlCxUd5qmU5uDJ1w1VLbDkobVK905A9cZZhYkfqGHg=')
	query = raw_input("Enter a search query ")
	pagesToBeCrawled = input("Enter the number of pages you would like to be crawled? ")
	fp.write('****************************The query searched for is:' + query + ", pages to be crawled: " + str(pagesToBeCrawled) + '\n')
	urlList, next_uri = bing.search(query, limit=10, format='json') # get the results
	for result in urlList:
		#initialUrls.append(result); # Add the initial lists to the list
		if (pages > pagesToBeCrawled):
				print 'We have successfully crawled',pagesToBeCrawled,'pages'
				break
		checkUrl(result.url)


# used to crawl the pages outward
# with the heap
# extract the pages with the highest the score from the heap and get the score for each url
# and download them
def crawl():
	global pagesToBeCrawled
	global pages
	global myHeap
	while not myHeap.empty() and (pages < pagesToBeCrawled):# traverse through the list while its not empty, and keep crawling while we havent reached the limit
		n = myHeap.get()# get the topmost element and traverse each of the links in this page
		for link in n.array:
			if pages > pagesToBeCrawled:
				print 'We have successfully crawled',pagesToBeCrawled,'pages'
				break
			checkUrl(link)






#lets download the pages
def checkUrl(url):
			#initialUrls.append(result.url); # Add the initial lists to the list
		#unicodedata.encode('ascii','ignore')
		try:
			# Now will see which sites not to crawl
			parsed_uri = urlparse(url)
			base = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri) # get base domain
			if not blackList(url,base): # if the url is not in the black list!
				if not url in encounteredUrls: # if we havent encountered it yet
					encounteredUrls[url] = url
					global pages
					global myHeap
					print 'Crawling ',url,pages
					opener = MyOpener() # used to change the user agent
					html = opener.open(url)
					if html != None: # open it here to ck if the page doesnt have errors
						#opener.retrieve(url,"/home/shah/Downloads/results/page " + str(pages)+ ".html")
						#print '=========== before soup'
						soup = BeautifulSoup(html.read(),"lxml") # parse the webpage
						x = soup.findAll(text = re.compile(query))
						n = Node(len(x),url) # creating new node for storing the values in the heap
						if n.score == 0:
							#meaning not relevant!
							return
						pages += 1 # increment the page here
						myHeap.put(n) # store it in the heap
						global fb
						fp.write(str(pages) + ', Crawling ' + url + ', Score: ' + str(n.score) +', Time: ' + str(datetime.datetime.now())+', Code: '+ str(html.getcode()) + '\n')
						#print '============== before for loop'
						for link in soup.find_all('a'):
							url =  str(unicode(link.get('href')).encode("UTF-8"))
							# ck if the url is in the black list or has a extention
							#url.encode('ascii','ignore')
							#print Crawlable(url)
							if Crawlable(url):
								if url.find('Http:') == -1 or url.find('www.') == -1: # not valid link, join it with the base
									n.appendUrl(urljoin(base,url))
								else: # we have a valid link
									n.appendUrl(url)
					else:
						print 'We encountered a None type!'
		except: 
		# # 	#print sys.exc_info()[0]
		# # 	#get error code
			#a= urllib.urlopen(url)
			fp.write('Crawling ' + url + 'Score:  Time: ' + str(datetime.datetime.now())+' Code: '+ '\n')
			print 'exception'

def blackList(base,url): # ck of the url has been blacklisted
	global blackListUrls
	if base in blackListUrls or url in blackListUrls:
		return True
	return False

def Crawlable(url):
	global badUrlExtentions
	for ext in badUrlExtentions: # crawl and ck if we encounter any of these extionsion, if we do, return false
		if url.find(ext) == 1:
			return False
	return True


#prints the urls for testing purposes
def printList():
	global myHeap
	while not myHeap.empty():# traverse through the list while its not empty
		n = myHeap.get()
		print n.name,' ',n.score





getTopTen() # get the top ten
# print 'going to crawl'
crawl() # start crawling outward
#printList()
fp.close()
# while not myHeap.empty():
# 	x =  myHeap.get()
# 	print x.score,x.name
