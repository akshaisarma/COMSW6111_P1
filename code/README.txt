Project 1 for COMS E6111 Advanced Database Systems

a) Your name and your partner's name and Columbia UNI

Yuan Du (yd2234)
Akshai Sarma (as4107)


b) A list of all the files that you are submitting:

* run.sh 		(a shell script that runs all the codes)
* UI.py 		(the main python script for the user interface and ranking)
* web_query.py 	(a python script for querying Bing API)
* stopwords.txt (a file containing stop word list)
* README.txt 	(this readme file)
* transcript.txt (a transcript for 3 test cases)

c) A clear description of how to run your program

Similar to the reference, run the following from the directory where you put all the scripts (NOTE: you must cd to that directory before running this command):

./run.sh <bing account key> <precision> <query>

, where:
<bing account key > is your Bing Search Account Key (see above)
<query> is your query, a list of words in single quotes (e.g., 'Milky Way')
<precision> is the target value for precision@10, a real between 0 and 1

For example, you can run this in CLIC machine:
cd /home/yd2234/ADB/proj1/code/COMSW6111_P1/code
./run.sh 'MWQrrA8YW+6ciAUTJh56VHz1vi/Mdqu0lSbzms3N7NY=' 0.9 'snow leopard'


d) A clear description of the internal design of your project

TODO...


e) A detailed description of your query-modification method

TODO...


f) Your Bing Search Account Key

MWQrrA8YW+6ciAUTJh56VHz1vi/Mdqu0lSbzms3N7NY=

g) Any other information you consider significant

We added a few more common contractions of stopwords in additon to our list of stopwords obtained
through the citation below.
	Stopwords list: Ranks NL. http://www.ranks.nl/resources/stopwords.html
