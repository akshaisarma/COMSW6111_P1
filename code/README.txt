Project 1 for COMS E6111 Advanced Database Systems

a) Your name and your partner's name and Columbia UNI

Yuan Du (yd2234)
Akshai Sarma (as4107)


b) A list of all the files that you are submitting:
* Makefile		 (instructions on how to run the code)
* run.sh 		 (a shell script that runs all the codes)
* UI.py 		 (the main python script for the user interface and ranking)
* web_query.py 	 (a python script for querying Bing API)
* stopwords.txt  (a file containing stop word list)
* README.txt 	 (this readme file)
* transcript.txt (a transcript for 3 test cases)

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


d) A clear description of the internal design of your project

TODO...


e) A detailed description of your query-modification method

We initially considered using Rocchio as our query augmentation. As we have
not indexed the space of all documents and don't have weights for words
(i.e. something like tf-idf), we decided to design our own algorithm based
off Rocchio and certain patterns that we noticed. The following were our key
observations/generalizations (in no particular order):

	1. Once we have relevant results, we can use the search engine's own precision@x, for the
	1 <= x < 10 results, to establish an order amongst the relevant and irrelevant results. For example,
	the words in a relevant result at position 1 may be more important than the words in a relevant
	result at position 10.

	2. Title words are generally more important than the words in the summary, as titles are generally
	a distillation of the subject matter.

	3. Capitalized words in the summary (does not work in the Title as mostly all are capitalized),
	are generally better important than the other words because they turn out to be nouns or keywords
	and are usually the focus of the relevant results.

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

f) Your Bing Search Account Key

MWQrrA8YW+6ciAUTJh56VHz1vi/Mdqu0lSbzms3N7NY=

g) Any other information you consider significant

We added a few more common contractions of stopwords in additon to our list of stopwords obtained
through the citation below.
	Stopwords list: Ranks NL. http://www.ranks.nl/resources/stopwords.html
