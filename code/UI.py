# Author: Yuan Du (yd2234@columbia.edu)
# Date: Sep 24, 2012
# Function: user interface for 
# Usage: python UI.py <AccountKey> <precision> <query>

import sys
from web_query import Web_search
from collections import defaultdict
import operator

# precision@10
topK = 10

# # Test standard input/output
# name = raw_input("Enter your name: ")
# print "Your name is "+name

class User_Interface(object):

	def __init__ (self, accountKey, precision, query):
		self.accountKey = accountKey
		self.precision = precision
		self.query = query
		self.searcher = Web_search() # searcher for Bing
		self.results = [] # search results (top K), initialzed to empty
		self.user_feedback = [] # user responds "Y"/"N"
		self.newWords = "" # new words augmented

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
		# xml_content = self.searcher.search_Bing(self.accountKey, topK, self.query)
		# TODO...
		xml_content = self.searcher.search_Bing_from_file(self.accountKey, topK, self.query)
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
			respond = raw_input("Relevant (Y/N)?")
			# print "Your respond is "+respond
			self.user_feedback.append(respond)

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
		for respond in self.user_feedback:
			if respond=='Y':
				correct_num = correct_num+1
		# get the number of total results
		total_num = len(self.results)

		# check the denominator 
		if (total_num<0):
			print "Error in feedback_summary: no search results returned for query="+self.query
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

	def reRanking(self):
		print "Indexing results ...."
		queryWords = self.query.lower().split(" ")
		word_count_dict = defaultdict(int)
		for i in range(len(self.results)):
			if self.user_feedback[i]=='Y':
				# relevant result
				result = self.results[i] 
				title = result[0]
				summary = result[1]
				
				# add words in title
				titleWords = title.split(" ")
				for word in titleWords:
					if (len(word)>0): 
						# filter query
						lower_word = word.lower()
						inQuery = False
						for queryWord in queryWords:
							if queryWord==lower_word:
								inQuery = True
								break
						if inQuery==False:
							word_count_dict[word] = word_count_dict[word]+1

				# add words in summary
				summaryWords = summary.split(" ")
				for word in summaryWords:
					if (len(word)>0): 
						# filter query
						lower_word = word.lower()
						inQuery = False
						for queryWord in queryWords:
							if queryWord==lower_word:
								inQuery = True
								break
						if inQuery==False:
							word_count_dict[word] = word_count_dict[word]+1

		print "Indexing results ...."

		newWords = ""
		# sort the counts by decreasing order and put in newWords
		index = 0
		# print word_count_dict
		# print queryWords
		for word, count in sorted(word_count_dict.iteritems(), key=operator.itemgetter(1), reverse=True):
			# print "word-count:"
			# print (word, count)

			newWords = newWords+" "+word
			index = index+1
			if index>=2:
				break

		print "Augmenting by " + newWords
		# check if no new words added, stop the procedure
		if len(newWords)<=0:
			print "Below desired precision, but can no longer augment the query"
			return False
		else:
			self.query = self.query+newWords
			return True

	def runIt(self):
		"""
		The main loop for user interface
		"""
		while (True):
			self.print_search_parameter()
			self.display_search()
			# check if reaching desired precision or no related results 
			ifContinue = self.feedback_summary()
			if (ifContinue==False):
				break
			ifContinue = self.reRanking()
			if (ifContinue==False):
				break


def usage():
	print """
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
