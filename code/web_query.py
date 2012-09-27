# Author: Yuan Du (yd2234@columbia.edu)
# Date: Sep 23, 2012
# Function: return the top K (e.g., top 10) search results from querying Bing
# Usage: python web_query.py <topK> <query>
# Output: top K results

import sys
import urllib2
import base64
import xml.dom.minidom as minidom

class Web_search(object):

	def __init__(self):
		self.bingUrl = ''
		self.results_len = 0

	def search_Bing(self, accountKey, topK, query):
		"""
		search via Bing API, and return the results in XML format
		"""
		self.bingUrl = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Web?Query=%27'+query+'%27&$top='+str(topK)+'&$format=Atom'
		# print self.bingUrl
		accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
		headers = {'Authorization': 'Basic ' + accountKeyEnc}
		req = urllib2.Request(self.bingUrl, headers = headers)
		response = urllib2.urlopen(req)
		content = response.read()
		#content contains the xml/json response from Bing. 
		# print content
		return content

	def search_Bing_from_file(self, accountKey, topK, query):
		document = "sample_result.xml"
		try:
			input = file(document,"r")
		except IOError:
			sys.stderr.write("ERROR: Cannot read inputfile %s.\n" % document)
			sys.exit(1)
		xmldata = input.read()
		return xmldata

	def parse_XML(self, xml):
		"""
		Returl the title/summary/url for each search result
		"""
		# doc = minidom.parseString(xml) # when input is string
		doc = minidom.parseString(xml)
		xml_entries = doc.getElementsByTagName("entry")

		results = []
		for entry in xml_entries:
			# get title/summary/url for each entry
			title = entry.getElementsByTagName("d:Title")[0].firstChild.data
			summary = entry.getElementsByTagName("d:Description")[0].firstChild.data
			url = entry.getElementsByTagName("d:Url")[0].firstChild.data
			plain_entry = [title, summary, url]
			results.append(plain_entry)

		self.results_len = len(results)
		return results

	def printResults(self, content):
		for entry in content:
			title = entry[0]
			summary = entry[1]
			url = entry[2]
			print "title:\n"+title
			print "summary:\n"+summary
			print "url:\n"+url
			print

def usage():
	print """
	python web_query.py <topK> <query>
	where <topK> is the number of results to be retrieved, and
		  <query> is the query to search in Bing.
	For example: python web_query.py 10 'gates'
	"""

if __name__ == "__main__":

	if len(sys.argv)!=3: # Expect exactly two arguments
		usage()
		sys.exit(2)

	# account key for bing (may be changed later)
	accountKey = 'MWQrrA8YW+6ciAUTJh56VHz1vi/Mdqu0lSbzms3N7NY='
	topK = int(sys.argv[1])
	query = sys.argv[2]

	# an example to use Web_search in order to get top K results (return title/summary/url)
	search = Web_search()
	# return the xml content
	xml_content = search.search_Bing(accountKey, topK, query)
	# parse xml for top K results (return [entry1, entry2,...] where each entry is [title, summary, url])
	results = search.parse_XML(xml_content)
	# print the results retrieved
	search.printResults(results)
