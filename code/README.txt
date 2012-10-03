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

Similar to the reference, run the following from the directory where you put all the scripts (NOTE: you must cd to that
directory before running this command):

./run.sh <bing account key> <precision> <query>

, where:
<bing account key > is your Bing Search Account Key (see above)
<query> is your query, a list of words in single quotes (e.g., 'Milky Way')
<precision> is the target value for precision@10, a real between 0 and 1

For example, on a CLIC machine:
cd /home/yd2234/ADB/proj1/code/COMSW6111_P1/code
./run.sh 'MWQrrA8YW+6ciAUTJh56VHz1vi/Mdqu0lSbzms3N7NY=' 0.9 'snow leopard'

You can run our scripts directly by the commands above, since we have already put our scripts under that directory.

-------------------------------------------------------------
d) A clear description of the internal design of your project

We have two python scripts: UI.py and web_query.py. The following are detailed descriptions for each of them.

1. web_query.py
This is a tool script for querying Bing API and parsing the XML results. The main functions include:
	* search_Bing: search via Bing API and return the results in XML format
	* parse_XML: parse the XML content from Bing API, and return the title/summary/url for each search result
	(Input: XML from function search_Bing; Output: a list of top 10 results with their titles, summaries and urls)
We will firstly call function search_Bing and then call function parse_XML.

2. UI.py
This is the main python script for the user interface and ranking. The main functions include:
	* runIt: the main loop for user interface.
	It wil repeatedly search the query (each time augmented by at most two new words) until desired precision reached,
	or can no longer augment the query.
	This function calls those functions step by step:
		- print_search_parameter (print the parameters for searching)
		- display_search (display search results by Bing API, and receive user feedback)
		- feedback_summary (summarize all the user feedbacks)
		- ranking (if the termination conditions are not satisfied, augment and reorder the query and repeat from
		  the whole procedure)
	(Detailed information for each of them are below)

	* print_search_parameter: prints the parameters for searching such as client key, query and desired precision

	* display_search: use the tool script web_query.py to search Bing by the query and display search results. Users
	  can give feedbacks through the user interface.

	* feedback_summary: compute the precision by retrieved results. Return True if more search is needed; otherwise
	  return False (if number of relevant results is 0, or desired precision is reached).

	* ranking: for each result, removes stopwords, ranks the word, augments the query and returns True if the query can
	  be augmented, otherwise returns False.

	* applyRanking: compute the ranking score for a given word. Applies our ranking algorithm, based on Rocchio,
	  depending on various factors, such as if it is a Title word, capitalized in the Summary etc.
	  It is called by the function ranking.

	* augmentQuery: adds up to two new words to the query. Returns True if it could, else False. Also, changes scores
	  for all the words to alpha*scores for next iteration.
	  It is called by function ranking.

	* reorderQuery: re-order the words in the expanded query, according to the co-occurance of word pairs in relevant
	  documents.
	  It is called in the end of function augmentQuery.

-------------------------------------------------------------
e) A detailed description of your query-modification method

We initially considered using Rocchio as our query augmentation. As we have not indexed the space of all documents and
don't have weights for words (i.e. something like tf-idf), we decided to design our own algorithm based on Rocchio
and certain patterns that we noticed. The list mentions scores and weights, which are how we judge words to be relevant.
In other words, the higher the score, the more relevant we consider to word. The following were our key observations
and generalizations (they are not in any order):

	1. Once we have relevant results, we can use the search engine's own precision@x, for the
	1 <= x < 10 results, to establish an order amongst the relevant and irrelevant results. For example, the words
 	in a relevant result at position 1 may be more important than the words in a relevant result at position 10.

	2. Title words are generally more important than the words in the summary, as titles are generally a distillation
	of the subject matter.

	3. Capitalized words in the summary (does not work in the Title as mostly all are capitalized), are generally
	more important than the other words because they turn out to be nouns or keywords and are usually the focus
	of the relevant results.

	4. Once weights are assigned to words and since we may augment by at most two, it is generally a
	bad idea to always choose two words to augment by. For instance, if the word with the highest scores
	is overwhelmingly higher than the second highest word, it may not be a good idea to augment with both
	and push the query down the wrong track. This is seen in the example of the query "bill", where by
	"gates" and "october" are the top two best words to augment by. However, adding "october" brings
	unnecessary results such as Astrology into the search pool. Of course, if the differences are not that
	great, you should include both words.

	5. Words are usually in both relevant and irrelevant queries. It does make sense to drop the scores of
	words that are in irrelevant results, however it should not be dropped by the same score as it was
	increased in a relevant result. This is so that we don't want to drop the score too much for relevant
	words in irrelevant results.

	6. The frequency of a word is a good indication of an important/relevant word. However, we do not have
	idf, so our weights must be a combination of the frequency and the ideas above and point 8 below.

	7. Words in the previous iterations should not overwhelmingly influence the current iteration.

	8. It is much better to remove stop words. Search Engines do this anyway at the cost of answering
	queries that use stop words.

	9. A simple but powerful way of reordering the query is to count the number of times each pair of
	query words appear next to each other in relevant results and re-arranging the query terms in
	decreasing order of this count.

Using these observations (some of which are directly from Rocchio's algorithm such as 5 and 7), here
is the overview of our query modification method:

In order to implement the ideas, we need a few constants. Since, we do not have enough time/resources
to determine ideal values for and tune the constants, we did so empirically after many test runs:

Below are the constants that we used in our algorithm, which map to the ideas listed above. The names
after the values in parantheses will be how we refer to them from now on.
--------------------------------- begin Constants -----------------------------------
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
--------------------------------- end Constants -----------------------------------

We maintain a dictionary of words (case-insenstive) and floating point values. The keys are the words
and the values are their scores. We do not distinguish relevant and irrelevant words. Our algorithm
is expected to score irrelevant words below relevant words. This makes our design simple.

Once we have the feedback and the top 10 results, for each result (except for the first
set of results, where we something slightly different), we go through the results, after removing punctuations,
as follows :

for each word, we adjust its score as follows (if it doesn't exist, its previous score is 0.0):
	if the word is a stopword and since we keep a list of stopwords (Citation below), we continue
	to the next word.

	if it is from a relevant result, we add either (rt or rs or rcs) * positionScale{position} to its score
	depending on whether it was a title, summary or capitalized summary word.

	if it is from a irrelevant result, we do (nrt or nrs or nrcs) * positionScale{position} respectively.

If this was the first iteration, it doesn't make sense to scale the words by their position, so for this
iteration, the position scaling factor is set to 1.0.

Note that the dictionary shrinks the frequency of the word and scoring (in both current and past iterations) to one
value. Even though we don't keep all the information, our algorithm assigns it a numerical value, keeping track of it
indirectly through the score.

Once all the words are processed, the top two words (that are not already in the query) are compared to see if
their ratio is greater than beta. If not, both words are added in the order of their scores else only the highest
word is added.

Finally, we multiply each score in the dictionary by the factor of alpha, so that this scores of this iteration does not
influence the subsequent iterations too much (exponential decay).

Using this algorithm, it is possible that we may end up picking a word that appears only in a non-relevant
result. We wish to justify this and how it is not so bad a thing. Your algorithm for instance stops when
you have precision != 0 but can't find any suitable words. The situation we are talking about is
illustrated with a toy example. Suppose, only one result was relevant and the other 9 weren't. The only word in this
result is "apple" but it also appears in all the other 9 results. As a result (ignoring the position scale - assume it
is the first iteration), its score will be 1* rs - 9*nrs or 1 - 8.1 or -7.1
Now assume, the word "banana" appears in 2 of the 9 non-relevant results. Its score will become -2*nrs or -1.8.

Our algorithm will then choose to augment by "banana". We claim that this is not so bad. The only other
option is stopping the algorithm immediately (as your implementation does). All that can happen by
augmenting with "banana", is that the next iteration may have a decrease in precision or even terminate
due to 0 precision. Our method, in this extreme example, instead of failing, tries to recover. So, we think that
it is reasonable to augment by words that only appear in non-relevant entries if the alternative is stopping.
Furthermore, this situation is quite rare and only occurs when there is no other suitable word in either the
title or the summary of relevant documents.

Finally, after the query is augmented, we now re-order the query using ideas discussed in Point 9. We use the
query results from the most recent iteration and build a dictionary of adjacency counts. That is, in both the
title and summary, we look at adjacent words and if they both appear in the query, we increment the count of
these words. In the end, we order by the final counts and rebuild the query in a loop using the following simple
rules:
	If the new reordered query being built is xyz (where xyz is any number of terms including no terms), we take
	the pair with the largest count left in the dictionary. Let this pair be represented as (w1, w2). There are
	three cases.

	1. If w1 is already in xyz and w2 is not. In that case, if w1 is currently 'z' in xyz, we want to add w2 immediately
	after to preserve the adjacency information, making the query xyw1 w2.If w1 is anywhere else, we do not want to
	insert w2 after it because 	we will be breaking the order set previously using a higher adjacency count.
	2. If w2 is already in xyz and w1 is not. Similar to above, only if w2 is 'x', should we prepend w1 to xyz and
	make the query w1 w2yz.
	3. If neither w1 or w2 is in the results, we simply append w1 and w2 in that order to the results (the highest
	adjacency count pair will be initially added this way)

	Finally, all words that are in the re-ordered query are added to the end of the query.

For example, when the query is 'gates' and a new word 'bill' is augmented, the method without re-ordering will return
'gates bill', while our algorithm can get potentially better results by using 'bill gates' instead. Since we only have
two words, we simply count the number of times bill and gates appear in that order against the other order (which does
not happen). The first order clearly wins and we are able to query "bill gates". A similar example is the 'snow leopard'
case, the query is augmented by 'mac x'. Our algorithm will get re-ordered result 'x snow leopard mac', since the phrase
'Mac OS X Snow Leopard' appears so often in relevant documents. "mac" is added to the end due to it not appearing
adjacent to any other query term. Granted, we can increase the chances of getting a semantically correct ordering by
looking for sequences that are more than just adjacent words, we also increase the chances of ordering it incorrectly.
Using our method guarantees that at least they are immediately adjacent and hence, possibly connected.

-------------------------------------------------------------
f) Your Bing Search Account Key

MWQrrA8YW+6ciAUTJh56VHz1vi/Mdqu0lSbzms3N7NY=

-------------------------------------------------------------
g) Any other information you consider significant

1.We added a few more common contractions of stopwords in additon to our list of stopwords obtained through
the citation below.
Stopwords list: Ranks NL. http://www.ranks.nl/resources/stopwords.html

2. According to our experiment, all the testcases will need ONLY ONE iteration of user-feedback before reaching the
perfect precision (that is, precision = 1.0).
Besides the three testcases in course page ('snow leopard', 'gates' and 'bill'), we have tested query [giants] both
for the New York Giants football team and the San Francisco Giants baseball team.
Those two teams share a lot of common words such as 'schedule'. In our program, "new york" or "san francisco" will
be augmented in each case.
