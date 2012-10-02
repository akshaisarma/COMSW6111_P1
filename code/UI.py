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
import unicodedata

# =============== CONSTANTS =================
# precision@10
topK = 10
# Path to file containing stop words
pwd = os.getcwd()
stopWordsPath = pwd+"/stopwords.txt"

# === Ranking algorithm constants ===

# Score multiplier for position in results. E.g. Result 1 -> Scale 1.09, Result 2 -> 1.08
base = 1.09
increment = 0.01
positionScale = {}
for k in range(0,10):
	positionScale[k] = base-increment*k

rTitleScale = 1.1 # Scaling for relevant Title words
rSummaryScale = 1.0 # Scaling for relevant Summary words
rCapSummaryScale = 1.15 # Scaling for relevant capitalized Summary words
nrTitleScale = 1.0 # Scaling for non-relevant Title words
nrSummaryScale = 0.9 # Scaling for non-relevant Summary words
nrCapSummaryScale = 0.95 # Scaling for non-relevant capitalized Summary words

# Constant for scaling word scores after iteration
alpha = 0.8

# Constant for adding only one word if the ratio of the top two words is above this limit
beta = 1.5
# =============== CONSTANTS =================

class User_Interface(object):

	def __init__ (self, accountKey, precision, query):
		self.accountKey = accountKey
		self.precision = precision
		self.query = query
		self.internalQuery = "+".join(query.split()) # query used for URL of Bing search
		self.searcher = Web_search() # searcher for Bing
		self.results = [] # search results (top K), initialzed to empty
		self.user_feedback = [] # user responds "Y"/"N"
		self.wordIndex = defaultdict(float) # index for our ranking algorithm
		self.firstIteration = True

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
		otherwise return False (if number of relevant results is 0, or desired precision is reached)
		"""
		print "FEEDBACK SUMMARY"
		print "Query "+self.query

		# get the number of correct results
		correct_num = 0
		for response in self.user_feedback:
			if response == 'y':
				correct_num = correct_num+1
		# get the number of total results
		total_num = len(self.results)

		# check the denominator
		if (total_num <= 0):
			print "No search results returned for the query"
			return False

		# if number of results <10, just terminate
		if (total_num < topK):
			print "Fewer than "+str(topK)+" results returned for the query"
			return False

		# precision of retrieved results
		pre = 1.0*correct_num/total_num
		print "Precision "+str(pre)

		# check if reaching the desired precision
		if self.precision <= pre:
			print "Desired precision reached, done"
			return False

		# still below the desired precision
		print "Still below the desired precision of "+str(self.precision)

		# if precision is 0, stop
		if (pre == 0.0):
			# To keep the output consistent with reference implementation
			print "Indexing results ...."
			print "Indexing results ...."
			print "Augmenting by "
			print "Below desired precision, but can no longer augment the query"
			return False
		return True

	def applyRanking(self, position, word, isTitleWord, isRelevant):
		"""
		Applies our ranking algorithm, based off Rocchio, depending on various factors,
		such as if it is a Title word, capitalized in the Summary etc.
		"""

		positionScore = positionScale[position]
		# Don't position scale the first results because we have no idea about relevance
		if (self.firstIteration):
			positionScore = 1.0
			self.firstIteration = False

		# Since it is a defaultdict, the entry will be created if it doesn't exist
		# Please read our README for details on our algorithm. The specifics are too
		# long to mention here.
		score = self.wordIndex[word.lower()]
		if isTitleWord:
			if isRelevant:
				score = score + rTitleScale * positionScore
			else:
				score = score - nrTitleScale * positionScore
		else:
			if word[0].isupper():
				if isRelevant:
					score = score + rCapSummaryScale * positionScore
				else:
					score = score - nrCapSummaryScale * positionScore
			else:
				if isRelevant:
					score = score + rSummaryScale * positionScore
				else:
					score = score - nrSummaryScale * positionScore
		self.wordIndex[word.lower()] = score
		return

	def reorderQuery(self):
		"""
		Re-order the words in the expanded query
		"""

		# constraints for the order of words, e.g., bill should be on the left of gates
		coOccurDict = defaultdict(int) # dictionary for the count of co-occurance pair
		queryWords = self.query.split()
		queryWordsLower = self.query.lower().split()

		# try all the relevant documents
		for i in range(len(self.results)):
			result = self.results[i]
			title = result[0]
			summary = result[1]

			# do only for relevant docs
			if self.user_feedback[i] != 'y':
				continue

			# Must be relevant results now
			# Remove punctuation and create lists of words
			titleWords = "".join(c for c in title if not unicodedata.category(c).startswith('P')).split()
			summaryWords = "".join(c for c in summary if not unicodedata.category(c).startswith('P')).split()

			# add co-occurance pair in title
			for i in range(len(titleWords)-1):
				currentWord = titleWords[i]
				nextWord = titleWords[i+1]

				# check if they are the identical words
				if currentWord.lower() == nextWord.lower():
					continue

				# checking whether current word and next word are in query
				if (currentWord.lower() in queryWordsLower) and (nextWord.lower() in queryWordsLower):
					# update the constraints in coOccurDict
					coOccurDict[(currentWord.lower(), nextWord.lower())] = coOccurDict[(currentWord.lower(), nextWord.lower())]+1

			# add co-occurance pair in summary
			for i in range(len(summaryWords)-1):
				currentWord = summaryWords[i]
				nextWord = summaryWords[i+1]

				# checking whether current word and next word are in query
				if (currentWord.lower() in queryWordsLower) and (nextWord.lower() in queryWordsLower):
					# update the constraints in coOccurDict
					coOccurDict[(currentWord.lower(), nextWord.lower())] = coOccurDict[(currentWord.lower(), nextWord.lower())]+1
		
		# sort by the count of co-occurance pairs
		sortedByLargest = sorted(coOccurDict.iteritems(), key=operator.itemgetter(1), reverse=True) 

		# add those constraints to the results for re-ordering
		results = [] # valid results for re-ordering

		for (w1, w2), count in sortedByLargest:
			# check if w2 appears in the existing results
			if w2 in results:
				# check if w2 in the beginning of existing results
				if (w2 == results[0]) and (w1 not in results):
					# append w2 in the beginning
					results.insert(0, w1)
				continue
			# check if w1 appears in the existing results
			if w1 in results:
				# check if w1 in the end of existing results
				if (w1 == results[len(results)-1]) and (w2 not in results):
					# append w2 in the end
					results.append(w2)
				continue

			# both w1 and w2 are not in existing results
			results.append(w1)
			results.append(w2)

		# add those words not in results
		for word in queryWordsLower:
			if word not in results:
				results.append(word)

		# re-write query and internal query
		self.query = " ".join(results)
		self.internalQuery = "+".join(results)


	def augmentQuery(self):
		"""
		Adds up to two new words to the query. Returns True if it could else False.
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

			# Want to only add one word if the first word is overwhelmingly more relevant
			# as we do not want to push the query down a wrong track. We add a small constant
			# to v as we do not want to divide by zero.
			if nWordsAdded == 1:
				if valueOfLargest/(v+0.001) > beta:
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

		print "Augmenting by " + newWords

		# If we did not get a new word, then we have to stop. Very unlikely.
		if nWordsAdded > 0:
			# re-order the words in query and return True
			self.reorderQuery()
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
			title = result[0]
			summary = result[1]

			# Remove punctuation and create lists of words
			titleWords = "".join(c for c in title if not unicodedata.category(c).startswith('P')).split()
			summaryWords = "".join(c for c in summary if not unicodedata.category(c).startswith('P')).split()

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

			# check if 0 precision or reached desired precision
			ifContinue = self.feedback_summary()
			if (ifContinue == False):
				break

			# check if we can no longer augment the query
			ifContinue = self.ranking()
			if (ifContinue == False):
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
