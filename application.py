# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from newsapi import NewsApiClient
import string
import operator
import json

# Init
newsapi = NewsApiClient(api_key='39f6b9e76d2743139dd3d54570e7ec90')
application = Flask(__name__)


@application.route('/')
def index():
	return application.send_static_file("index.html")

@application.route('/sources')
def get_sources():
	sources = newsapi.get_sources(language="en", country="us")
	# print(sources)
	return json.dumps(sources)


@application.route('/top_headlines_sources')
def get_top_headlines_sources():
	# print(request.args)
	source = request.args.get('source', None)
	if source == None:
		top_headlines = newsapi.get_top_headlines(sources=source, page_size=30, country="us", language="en" )
	else:
		top_headlines = newsapi.get_top_headlines(sources=source, page_size=30)
	return json.dumps(top_headlines)

@application.route("/top_frequent_words")
def get_top_frequent_words():
	stopwords_file = open('static/stopwords_en.txt')
	stopwords_set = set()
	for word in stopwords_file:
		word = word.strip()
		stopwords_set.add(word)
	punctuation_set = set(string.punctuation)
	stopwords_set = stopwords_set.union(punctuation_set)
	stopwords_set.add("—")
	top_articles = newsapi.get_top_headlines(page_size=30, language="en", country="us")
	top_articles = top_articles['articles']
	frequent_words = dict()
	titles=[]
	top_words = []
	for x in top_articles:
		if x['title'] is not None:
			titles.append(x['title'])
	word_list=[]
	for t in titles:
		words = t.split(" ")
		for w in words:
			if not w.isdigit():
				word_punct=""
				for wd in w:
					if wd not in string.punctuation:
						word_punct+=wd
				if word_punct not in stopwords_set:
					word_list.append(word_punct)

	for w in word_list:
		if w:
			if frequent_words.get(w):
				frequent_words[w] += 1
			else:
				frequent_words[w] = 1
	sortedwords = sorted(frequent_words.items(), key=operator.itemgetter(1), reverse=True)
	#print(sortedwords)

	for i in sortedwords[0:30]:
		word_dict = {}
		word_dict['size'] = i[1]
		word_dict['word'] = i[0]
		#print(word_dict)
		top_words.append(word_dict)

	frequent_words = {"words":top_words}
	# print(frequent_words)
	return json.dumps(frequent_words)


@application.route('/news_content', methods=['GET','POST'])
def get_news_content():
	search_keyword = request.args.get('search_keyword', )
	start_date = request.args.get('start_date')
	end_date = request.args.get('end_date')
	news_category = request.args.get('news_category')
	if(news_category == 'all'):
		news_category = None
	news_source = request.args.get('news_source')
	if(news_source=='all'):
		news_source = None
	try:
		all_articles = newsapi.get_everything(q=search_keyword, sources=news_source, from_param=start_date, to=end_date, language='en', sort_by='publishedAt', page_size=30)
	except Exception as e:
		out_error={'status':'error','err_msg':e.get_message()}
		return json.dumps(out_error)
	return json.dumps(all_articles)

@application.route('/filter_sources')
def filter_sources():
	news_category = request.args['news_category']
	sources = newsapi.get_sources(category=news_category, language='en', country ='us')
	return json.dumps(sources)

if __name__ == "__main__":
	application.run()