#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import nltk
import re
import time

USER_AGENT = {'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}

def google_results_urls(search_term, number_results, language_code, site):
	"""returns an array of URLs from the google results for a search string"""
	# make sure the inputs have the right types
	assert isinstance(search_term, str), 'Search term must be a string'
	assert isinstance(number_results, int), 'Number of results must be an integer'
	assert isinstance(site, str), 'Site must be a string'

	query_string = search_term.replace(' ', '+') + ' site:' + site

	# get google results (tbm: nws means google news only)
	payload = {'tbm': 'nws', 'q': query_string, 'num': number_results, 'hl': language_code}

	response = requests.get('https://www.google.com/search', params=payload, headers=USER_AGENT)

	soup = BeautifulSoup(response.text, 'html.parser')

	# only grab HTTP(S) links
	url_regex = "^https?://"
	links = [link.get('href') for link in soup.findAll('a', attrs={'href': re.compile(url_regex)})]
	# see if they're from the right site
	return [l for l in links if (l.startswith("https://www." + site) or l.startswith("http://www." + site))]

def get_text(search_result_links, sleep_time):
	"""grab the text content of each link in an array, then spit out a new array
	that contains strings with the text of each link"""
	output = []
	# grab the contents of each link
	def get_results(search_result_links, sleep_time=30):
		results = []
		for l in search_result_links:
			results.append(requests.get(l, headers=USER_AGENT))
			# wait N seconds then scrape next link
			time.sleep(sleep_time)
		return results
	# one-liner that doesn't pause
	#results = [requests.get(l, headers=USER_AGENT) for l in search_result_links]

	# pull the text contents for each URL and put each URL's contents in the array as a string
	for r in get_results(search_result_links, 5):
		soup = BeautifulSoup(r.text, 'html.parser')
		output.append(" ".join([p.text for p in soup.find_all("p")]))

	return output
	# one-liner
	#return [BeautifulSoup(r, 'html.parser').get_text() for r in results]

def get_sentiment(text_array):
	"""do sentiment analysis on the array of strings"""
	sentiment_data = [TextBlob(t).sentiment for t in text_array]

	def average_polarity(sentiments):
		p = [s.polarity for s in sentiments]
		return sum(p)/len(p)

	def average_subjectivity(sentiments):
		sb = [s.subjectivity for s in sentiments]
		return sum(sb)/len(sb)

	return [average_polarity(sentiment_data), average_subjectivity(sentiment_data)]

def avg_sentence_length(text_array):
	"""parse out sentences from paragraphs and return average sentence length"""
	# sentence lengths
	lengths = []

	for t in text_array:
		# get list of sentences
		sentences = nltk.sent_tokenize(t)
		# get word totals for sentences
		words = [nltk.word_tokenize(s) for s in sentences]
		for w in words:
			lengths.append(len(w))
	
	#return average length
	return sum(lengths)/len(lengths)

def assemble_results(text_data, label):
	"""just a dumb way to see the results, will add Bokeh visuals later"""
	output = ""
	output += "Average sentiment [polarity, subjectivity] for " + label + "\n"
	output += str(get_sentiment(text_data)) + "\n"
	output += "Average sentence length for " + label + "\n"
	output += str(avg_sentence_length(text_data)) + "\n"
	return output

# let's get some results!
# reminder: params are search string, number of results pages, language, URL to scrape for
cnn = get_text(google_results_urls("immigration", 3, "en", "cnn.com"), 5)
# Fox seems to prefer slower requests
fox = get_text(google_results_urls("immigration", 3, "en", "foxnews.com"), 10)
#usatoday = get_text(google_results_urls("Trump", 2, "en", "usatoday.com"), 5)
#msnbc = get_text(google_results_urls("Trump", 2, "en", "msnbc.com"), 5)

#print the things
print(assemble_results(cnn, "CNN"))
print(assemble_results(fox, "Fox News"))
#print(assemble_results(usatoday, "USA Today"))
#print(assemble_results(msnbc, "MSNBC"))