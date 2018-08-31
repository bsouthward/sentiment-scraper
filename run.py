#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import nltk
import re

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

def google_results_urls(search_term, number_results, language_code, site):
	"""returns an array of URLs from the google results for a search string"""
	# make sure the inputs have the right types
	assert isinstance(search_term, str), 'Search term must be a string'
	assert isinstance(number_results, int), 'Number of results must be an integer'
	assert isinstance(site, str), 'Site must be a string'
	escaped_search_term = search_term.replace(' ', '+')
	search_in_site = escaped_search_term + '+site:' + site
	
	# get google results
	payload = {'q': search_in_site, 'num': number_results, 'hl': language_code}

	response = requests.get('https://www.google.com/search', params=payload, headers=USER_AGENT)

	soup = BeautifulSoup(response.text, 'html.parser')

	# only grab HTTPs links
	url_regex = "^https?://"
	links = [link.get('href') for link in soup.findAll('a', attrs={'href': re.compile(url_regex)})]

	# see if they're from the right site
	return [l for l in links if l.startswith("https://www." + site) or l.startswith("http://www." + site)]

def get_text(search_result_links):
	"""grab the text content of each link in an array, then spit out a new array
	that contains strings with the text of each link"""
	output = []
	# grab the contents of each link
	results = [requests.get(l, headers=USER_AGENT) for l in search_result_links]

	# pull the text contents for each URL and put each URL's contents in the array as a string
	for r in results:
		soup = BeautifulSoup(r.text, 'html.parser')
		output.append("".join([p.text for p in soup.find_all("p")]))
	return output

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

# let's get some results!
cnn = get_text(google_results_urls("Trump", 2, "en", "cnn.com"))
fox = get_text(google_results_urls("Trump", 2, "en", "foxnews.com"))

# print the things
print("Average sentiment for CNN [polarity, subjectivity]:")
print(get_sentiment(cnn))
print("Average sentence length for CNN:")
print(avg_sentence_length(cnn))

print("Average sentiment for Fox News [polarity, subjectivity]:")
print(get_sentiment(fox))
print("Average sentence length for Fox News:")
print(avg_sentence_length(fox))