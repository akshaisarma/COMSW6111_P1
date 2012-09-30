# Author: Yuan Du (yd2234@columbia.edu)
# Author: Akshai Sarma (as4107@columbia.edu)
# Date: Sep 24, 2012
# Function: user interface for Bing search
# Usage: python UI.py <AccountKey> <precision> <query>

import sys
from web_query import Web_search
from collections import defaultdict
import operator
import string
import os

# =============== CONSTANTS =================
# pwd
pwd = os.getcwd()

# precision@10
topK = 10
# Path to file containing stop words
stopWordsPath = pwd+"/stopwords.txt"

# Ranking algorithm constants

# Score multiplier for position in results. E.g. Result 1 -> Scale 1.09
# positionScale = { k:1.09-0.01*k for k in range(0,10) }
positionScale = defaultdict(float)

rTitleScale = 1.1 # Scaling for relevant Title words
rSummaryScale = 1.0 # Scaling for relevant Summary words
rCapSummaryScale = 1.15 # Scaling for relevant capitalized Summary words
nrTitleScale = 1.0 # Scaling for non-relevant Title words
nrSummaryScale = 0.9 # Scaling for non-relevant Summary words
nrCapSummaryScale = 0.95 # Scaling for non-relevant capitalized Summary words

# Constant for scaling query results after iteration
alpha = 0.8

# Constant for adding only one word if the ratio of the top two words is above this limit
beta = 1.5
# =============== CONSTANTS =================

class User_Interface(object):

	def __init__ (self, accountKey, precision, query):
		# initialize positionScale
		for k in range(0,10):
			positionScale[k] = 1.09-0.01*k

		# initialize other parameters
		self.accountKey = accountKey
		self.precision = precision
		# self.query = query.lower()
		self.query = query # no need to lower, lower during augmenting

		self.internalQuery = "+".join(query.lower().split()) # query used for URL of Bing search
		self.searcher = Web_search() # searcher for Bing
		self.results = [] # search results (top K), initialzed to empty
		self.user_feedback = [] # user responds "Y"/"N"
		self.newWords = "" # new words augmented
		self.wordIndex = defaultdict(float) # index for our ranking algorithm
		# Load set of stop words
		with open(stopWordsPath, 'r') as temp:
			self.stopWords = frozenset(temp.read().split())

	def print_search_parameter(self):
		"""
		Print parameters for search
		"""
		print "Parameters:"
		print "Client key  = "+self.accountKey
		print "Query       = "+self.query
		print "Precision   = "+str(self.precision)

	def display_search(self):
		"""
		Search Bing by the query and display search results
		"""
		# call functions in web_query.py for Bing search and XML parse
		xml_content = self.searcher.search_Bing(self.accountKey, topK, self.internalQuery)
		# TODO...
		# xml_content = self.searcher.search_Bing_from_file(self.accountKey, topK, self.query)
		self.results = self.searcher.parse_XML(xml_content)

		# print URL for Bing Search
		print "URL: "+self.searcher.bingUrl
		print "Total no of results : "+str(self.searcher.results_len)
		print "Bing Search Results:"
		print "======================"
		# print each result
		self.user_feedback = []
		index = 0
		for entry in self.results:
			index = index+1

			title = entry[0]
			summary = entry[1]
			url = entry[2]
			print "Result "+str(index)+"\n[\n URL: "+url+"\n Title: "+title+"\n Summary: "+summary+"\n]\n"
			response = raw_input("Relevant (Y/N)?")
			self.user_feedback.append(response.lower())

		print "======================"

	def feedback_summary(self):
		"""
		Compute the precision by retrieved results
		Return True if more search is needed
		otherwise return False (if number of retrieved results is 0, or desired precision is reached)
		"""
		print "FEEDBACK SUMMARY"
		print "Query "+self.query
		# get the number correct results
		correct_num = 0
		for response in self.user_feedback:
			if response == 'y':
				correct_num = correct_num+1
		# get the number of total results
		total_num = len(self.results)

		# if nothing was relevant
		# if correct_num == 0:
		# 	print "No result was relevant. Quitting..."
		# 	return False

		# check the denominator
		if (total_num<=0):
			print "No search results returned for the query"
			return False

		# if number of results <10, just terminate
		if (total_num<topK):
			print "Fewer than "+str(topK)+" results returned for the query"
			return False

		# precision by retrieved results
		pre = 1.0*correct_num/total_num
		print "Precision "+str(pre)
		# check if reaching the desired precision
		if self.precision<=pre:
			print "Desired precision reached, done"
			return False
		else:
			print "Still below the desired precision of "+str(self.precision)
			return True

	def applyRanking(self, position, word, isTitleWord, isRelevant):
		"""
		Applies our ranking algorithm, based off Rocchio, depending on various factors,
		such as if it is a Title word, capitalized in the Summary etc.
		"""

		# Since it is a defaultdict, the entry will be created if it doesn't exist
		score = self.wordIndex[word.lower()]
		if isTitleWord:
			if isRelevant:
				score = score + rTitleScale * positionScale[position]
			else:
				score = score - nrTitleScale * positionScale[position]
		else:
			if word[0].isupper():
				if isRelevant:
					score = score + rCapSummaryScale * positionScale[position]
				else:
					score = score - nrCapSummaryScale * positionScale[position]
			else:
				if isRelevant:
					score = score + rSummaryScale * positionScale[position]
				else:
					score = score - nrSummaryScale * positionScale[position]
		self.wordIndex[word.lower()] = score
		return

	def augmentQuery(self):
		"""
		Adds upto two new words to the query. Returns True if it could else False.
		Also, changes values to alpha*values for next iteration
		"""
		queryWords = frozenset(self.query.lower().split())
		nWordsAdded = 0

		# Sort by score of the word in index
		sortedByLargest = sorted(self.wordIndex.iteritems(), key=operator.itemgetter(1), reverse=True)
		valueOfLargest = 0.0

		# keep track of the new words augmented
		newWords = ""

		# check all the words from highest score
		for k,v in sortedByLargest:
			# filter those already in the query
			if k in queryWords:
				continue

			# Want to add words only if it gets score>0
			if v<=0.0:
				break
			# Want to only add one word if the first word is overwhelmingly more relevant
			# as we do not want to push the query down a wrong track
			if nWordsAdded == 1 and v != 0.0:
			# if nWordsAdded == 1 and v > 0.0:
				if valueOfLargest/v > beta:
					break

			self.query = self.query + " " + k.lower()
			self.internalQuery = self.internalQuery + "+" + k.lower()
			valueOfLargest = v
			nWordsAdded+=1
			newWords = newWords+" "+k.lower()

			if nWordsAdded == 2:
				break

		# Change scores for next iteration
		for w in self.wordIndex.iterkeys():
			self.wordIndex[w] = self.wordIndex[w] * alpha

		print "Augmenting by "+newWords

		# If we did not get a new word, then we have to stop. Very unlikely.
		if nWordsAdded > 0:
			return True
		else:
			return False

	def ranking(self):
		"""
		For each result, removes stopwords, ranks the word, augments the query
		and returns True if successful else False
		"""
		print "Indexing results ...."
		
		for i in range(len(self.results)):
			result = self.results[i]
			title = result[0].encode('ascii', 'ignore')
			summary = result[1].encode('ascii', 'ignore')
			# Remove punctuation and create lists of words
			titleWords = title.translate(None, string.punctuation).split()
			summaryWords = summary.translate(None, string.punctuation).split()

			for tw in titleWords:
				if tw.lower() in self.stopWords:
					continue
				if self.user_feedback[i] == 'y':
					self.applyRanking(i, tw, True, True)
				else:
					self.applyRanking(i, tw, True, False)

			for sw in summaryWords:
				if sw.lower() in self.stopWords:
					continue
				if self.user_feedback[i] == 'y':
					self.applyRanking(i, sw, False, True)
				else:
					self.applyRanking(i, sw, False, False)

		print "Indexing results ...."

		return self.augmentQuery()

	def runIt(self):
		"""
		The main loop for user interface
		"""
		# repeat searching until desired precision reached, or no longer augment the query
		while (True):
			self.print_search_parameter()
			self.display_search()
			# check if reaching desired precision
			ifContinue = self.feedback_summary()
			if (ifContinue==False):
				break
			# check if precision=0 or no longer augment the query
			ifContinue = self.ranking()
			if (ifContinue==False):
				# print "Unable to augment query as all words are in query. Exiting ..."
				print "Below desired precision, but can no longer augment the query"
				break


def usage():
	print """
	Usage:
	python UI.sh <accountKey> <precision> <query>
	where <accountKey> is the Bing Search Account Key,
	<precision> is the target value for precision@10, a real between 0 and 1, and
	<query> is the query, a list of words in single quotes (e.g., 'Milky Way').
	For example: python UI.py 'MWQrrA8YW+6ciAUTJh56VHz1vi/Mdqu0lSbzms3N7NY=' 0.9 'gates'
	"""

if __name__ == "__main__":

	if len(sys.argv)!=4: # Expect exactly 3 arguments and the python script
		usage()
		sys.exit(2)
		# an example to use Web_search in order to get top K results (return title/summary/url)

	accountKey = sys.argv[1]
	precision = float(sys.argv[2])
	query = sys.argv[3]

	ui = User_Interface(accountKey, precision, query)
	ui.runIt()
