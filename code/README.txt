Project 1 for COMS E6111 Advanced Database Systems
-------------------------------------------------------------
a) Your name and your partner's name and Columbia UNI

Yuan Du (yd2234)
Akshai Sarma (as4107)

-------------------------------------------------------------
b) A list of all the files that you are submitting:
* Makefile		 (instructions on how to run the code)
* run.sh 		 (a shell script that runs all the codes)
* UI.py 		 (the main python script for the user interface and ranking)
* web_query.py 	 (a python script for querying Bing API)
* stopwords.txt  (a file containing stop word list)
* README.txt 	 (this readme file)
* transcript.txt (a transcript for 3 test cases)

-------------------------------------------------------------
c) A clear description of how to run your program

Similar to the reference, run the following from the directory where you put all the scripts (NOTE: you must cd to that directory before running this command):

./run.sh <bing account key> <precision> <query>

, where:
<bing account key > is your Bing Search Account Key (see above)
<query> is your query, a list of words in single quotes (e.g., 'Milky Way')
<precision> is the target value for precision@10, a real between 0 and 1

For example, on a CLIC machine:
cd /home/yd2234/ADB/proj1/code/COMSW6111_P1/code
./run.sh 'MWQrrA8YW+6ciAUTJh56VHz1vi/Mdqu0lSbzms3N7NY=' 0.9 'snow leopard'

-------------------------------------------------------------
d) A clear description of the internal design of your project

We have two python scripts: UI.py and web_query.py. The following are detailed description for each of them.

1. web_query.py 
This is a tool script for querying Bing API and parsing the XML results. The main functions include:
	* search_Bing: search via Bing API and return the results in XML format 
	* parse_XML: parse the XML content from Bing API, and return the title/summary/url for each search result
	(Input: XML from function search_Bing; Output: a list of top 10 results with their titles, summaries and urls)
It will firstly call function search_Bing and then call function parse_XML.

2. UI.py
This is the main python script for the user interface and ranking. The main functions include:
	* runIt: the main loop for user interface. 
	It wil repeatedly search the query (each time augmented by at most two new words) until desired precision reached, or can no longer augment the query.
	This function calls those functions step by step:
		- print_search_parameter (print the parameters for searching)
		- display_search (display search results by Bing API, and receive user feedback)
		- feedback_summary (summarize all the user feedbacks)
		- ranking (if the termination conditions are not satisfied, augment the query and repeat from the whole procedure)
	(Detailed information for each of them are in the following.)

	* print_search_parameter: print parameters for searching such as client key, query and desired precision

	* display_search: use the tool script web_query.py to search Bing by the query and display search results. Users can give feedbacks by user interface.

	* feedback_summary: compute the precision by retrieved results. Return True if more search is needed; otherwise return False (if number of relevant results is 0, or desired precision is reached)

	* ranking: for each result, removes stopwords, ranks the word, augments the query and returns True if the query can be augmented, otherwise returns False

	* applyRanking: compute the ranking score for a given word. Applies our ranking algorithm, based on Rocchio, depending on various factors, such as if it is a Title word, capitalized in the Summary etc.
	It is called by function ranking.

	* augmentQuery: adds up to two new words to the query. Returns True if it could else False. Also, changes scores for all the words to alpha*scores for next iteration.
	It is called by function ranking.


-------------------------------------------------------------
e) A detailed description of your query-modification method

We initially considered using Rocchio as our query augmentation. As we have
not indexed the space of all documents and don't have weights for words
(i.e. something like tf-idf), we decided to design our own algorithm based
on Rocchio and certain patterns that we noticed. The list mentions scores and weights,
which are how we judge words to be relevant. In other words, the higher the score, the more relevant we consider to word. The following were our key observations/generalizations (in no particular order):

	1. Once we have relevant results, we can use the search engine's own precision@x, for the
	1 <= x < 10 results, to establish an order amongst the relevant and irrelevant results. For example, the words in a relevant result at position 1 may be more important than the words in a relevant result at position 10.

	2. Title words are generally more important than the words in the summary, as titles are generally a distillation of the subject matter.

	3. Capitalized words in the summary (does not work in the Title as mostly all are capitalized), are generally better important than the other words because they turn out to be nouns or keywords and are usually the focus of the relevant results.

	4. Once weights are assigned to words and since we may augment by at most two, it is generally a
	bad idea to always choose two words to augment by. For instance, if the word with the highest scores
	is overwhelmingly higher than the second highest way, it may not be a good idea to augment with both
	and push the query down the wrong track. This is seen well in the example of the query "bill", where by
	"gates" and "october" are the top two best words to augment by. However, adding "october" brings
	unnecessary results such as Astrology into the search pool. Of course, if the differences are not that
	great, you should include both words.

	5. Words are usually in both relevant and irrelevant queries. It does make sense to drop the scores of
	words that are in irrelevant results, however it should not be dropped by the same score as it was
	increased in a relevant result. This is so that we don't want to drop the score too much for relevant
	words in irrelevant results.

	6. The frequency of a word is a good indication of an important/relevant word. However, we do not have
	idf, so our weights must be a combination of the frequency and the ideas above.

	7. Words in the previous iterations should not overwhelmingly influence the current iteration .

	8. It is much better to remove stop words. Search Engines do this anyway at the cost of answering
	queries that use stop words.

Using these observations (some of which are directly from Rocchio's algorithm such as 5 and 7), here
is the overview of our query modification method:

In order to implement the ideas, we need a few constants. Since, we do not have enough time/resources
to determine ideal values for the constants, we did so emperically after a few test runs:

Below are the constants that we used in our algorithm, which map to the ideas listed above. The names
after the values in parantheses will be how we refer to them from now on.
--------------------------------- Constants -----------------------------------
Constant Factor for position in results. E.g. Result 1 -> Scale 1.09, Result 2 -> 1.08
positionScale{1..10} = {1.09, 1.08, ... 1.0}

Scaling Factor for Relevant Title Words   					= 1.1  (rt)
Scaling Factor for Relevant Summary Words 					= 1.0  (rs)
Scaling Factor for Relevant capitalized Summary words		= 1.15 (rcs)
Scaling Factor for non-Relevant Title Words					= 1.0  (nrt)
Scaling Factor for non-Relevant Summary Words 				= 0.9  (nrs)
Scaling Factor for non-Relevant capitalized Summary words	= 0.95 (nrcs)

Constant for scaling word scores after iteration			= 0.8  (alpha)

Constant ratio that the top two highest scores must
exceed in order for only the top word to be added			= 1.5  (beta)
--------------------------------- Constants -----------------------------------

We maintain a dictionary of words (case-insenstive) and floating point values. The keys are the words
and the values are their scores. We do not distinguish relevant and irrelevant words. Our algorithm
is expected to score irrelevant words below relevant words. This makes our design simple.

Once we have the feedback and the top 10 results, for each result (except for the first
set of results, where we something slightly different), we go through the results
as follows :

for each word, we adjust its score as follows (if it doesn't exist, its previous score is 0.0):
	if the word is a stopword and since we keep a list of stopwords (Citation below), we continue
	to the next word.

	if it is from a relevant result, we add either (rt or rs or rcs) * positionScale{position} to its score
	depending on whether it was a title, summary or capitalized summary word.

	if it is from a irrelevant result, we do (nrt or nrs or nrcs) * positionScale{position} respectively.

If this was the first iteration, it doesn't make sense to scale the words by their position, so for this
iteration, the positionScale is set to 1.0.

Note that the dictionary shrinks the frequency of the word and scoring (in both current and past iterations) to one
value. Even though we don't keep all the information, our algorithm assigns it a numerical value, keeping track of it
indirectly through the score.

Once all the words are processed, the top two words (that are not already in the query) are compared to see if
their ratio is greater than beta. If not, both words are added in the order of their scores else only the highest
word is added.

Finally, we multiply each score in the dictionary by the factor of alpha, so that this iteration does not
influence the subsequent iterations too much (exponential decay).

-------------------------------------------------------------
f) Your Bing Search Account Key

MWQrrA8YW+6ciAUTJh56VHz1vi/Mdqu0lSbzms3N7NY=

-------------------------------------------------------------
g) Any other information you consider significant

1. We added a few more common contractions of stopwords in additon to our list of stopwords obtained through the citation below.
	Stopwords list: Ranks NL. http://www.ranks.nl/resources/stopwords.html

2. According to our experiment, all the testcases will need ONLY ONE iteraction of user-feedback before reaching the perfect precision (that is, precision=1.0).
Besides the three testcases in course page ('snow leopard', 'gates' and 'bill'), we have tested query [giants] both for the New York Giants football team and the San Francisco Giants baseball team. 
Those two teams share a lot of common words such as 'schedule'. In our program, "new york" or "san francisco" will be augmented in each case.
