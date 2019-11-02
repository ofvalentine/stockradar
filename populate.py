# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import re
import environs
import psycopg2
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import requests
from textblob import Word
from urllib.request import Request, urlopen
import os
import collections

# CONNECT TO DATABASE
is_production = os.environ.get('IS_HEROKU', None)

if is_production:
    connection = psycopg2.connect(user=os.environ.get('USER'), password=os.environ.get('PASSWORD'),
                                  host=os.environ.get('HOST'), port="5432", database=os.environ.get('DATABASE'))
else:
    env = environs.Env()
    env.read_env()
    connection = psycopg2.connect(user=env.str('USER'), password=env.str('PASSWORD'),
                                  host=env.str('HOST'), port="5432", database=env.str('DATABASE'))

cursor = connection.cursor()
query = "INSERT INTO headlines (SOURCE, HEADLINE, KEYWORDS, LINK) VALUES (%s,%s,%s,%s);"

# SET UP IGNORE WORDS
ignore_words = set(stopwords.words('english'))
plural_words = ['jobs', 'stocks', 'markets', '']


# EXTRACT KEYWORDS FROM HEADLINE
def get_keywords(headline):
    headline = re.sub(r"-", ' ', headline)  # space for dash
    headline = re.sub(r"\\n|\\t|(\b[A-Z]+\s?\d?(:?[A-Z]+)?\b)|'s|’s|([^A-Za-z ])", '', headline)  # remove special char.
    keywords = [word for word in headline.lower().split() if word not in ignore_words]  # remove stopwords
    keywords = [Word(word).singularize() for word in keywords]
    return keywords


def clean(headline):
    return re.sub(r"(|\\r|\\n|\b[A-Z]+\s?\d?(:?[A-Z]+)?\b-)", '', headline)


# REUTERS MARKETS
html = requests.get('https://www.reuters.com/finance/markets')
soup = BeautifulSoup(html.text, "html.parser")
headlines_and_links = [(title.get_text(), "https://www.reuters.com" + title['href']) for title in
                       soup.find_all("a", href=re.compile("article"))[1:]]
for headline, link in headlines_and_links:
    cursor.execute(query, ("Reuters", clean(headline.strip()), get_keywords(headline), link))

# WSJ MARKETS
html = requests.get('https://www.wsj.com/news/markets')
soup = BeautifulSoup(html.text, "html.parser")
headlines_and_links = [(title.get_text(), title['href']) for title in
                       soup.find_all("a", class_="wsj-headline-link", href=re.compile("articles"))]
for headline, link in headlines_and_links:
    cursor.execute(query, ("WSJ", clean(headline.strip()), get_keywords(headline), link))

# YAHOO FINANCE
html = requests.get('https://finance.yahoo.com/topic/stock-market-news')
soup = BeautifulSoup(html.text, "html.parser")
headlines_and_links = [(title.get_text(), "https://finance.yahoo.com" + title['href']) for title in
                       soup.find_all("a", href=re.compile("news"))]
for headline, link in headlines_and_links:
    cursor.execute(query, ("Yahoo", clean(headline.strip()), get_keywords(headline), link))

# CNBC FINANCE
html = requests.get('https://www.cnbc.com/finance/')
soup = BeautifulSoup(html.text, "html.parser")
headlines_and_links = [(title.get_text(), title['href']) for title in
                       soup.find_all("a", class_="Card-title")]
for headline, link in headlines_and_links:
    cursor.execute(query, ("CNBC", clean(headline.strip()), get_keywords(headline), link))

# MARKETWATCH
html = requests.get('https://www.marketwatch.com/')
soup = BeautifulSoup(html.text, "html.parser")
headlines_and_links = [(title.get_text(), title['href']) for title in
                       soup.find_all("a", class_="link", href=re.compile("story"))]
for headline, link in headlines_and_links:
    cursor.execute(query, ("MarketWatch", clean(headline).strip(), get_keywords(headline), link))

# INDIA TIMES ET
html = requests.get('https://economictimes.indiatimes.com/markets')
soup = BeautifulSoup(html.text, "html.parser")
headlines_and_links = [(title.get_text(), "https://economictimes.indiatimes.com" + title['href']) for title in
                       soup.find_all("a", href=re.compile("^\\/+(markets)+\\/+\\w+\\/+(news)"))]
for headline, link in headlines_and_links:
    if headline:
        cursor.execute(query, ("India Times ET", clean(headline).strip(), get_keywords(headline), link))

# FINANCIAL TIMES
html = requests.get('https://www.ft.com/markets')
soup = BeautifulSoup(html.text, "html.parser")
headlines_and_links = [(title.get_text(), "https://www.ft.com" + title['href']) for title in
                       soup.find_all("a", attrs={'data-trackable': "heading-link"})]
for headline, link in headlines_and_links:
    cursor.execute(query, ("FT", clean(headline).strip(), get_keywords(headline), link))

# FINANCIAL NEWS LONDON
html = requests.get('https://www.fnlondon.com/')
soup = BeautifulSoup(html.text, "html.parser")
headlines_and_links = [(title.get_text(), title['href']) for title in
                       soup.find_all("a", class_=re.compile("FinancialNewsTheme--headline-link--"))]
for headline, link in headlines_and_links:
    cursor.execute(query, ("FN London", clean(headline).strip(), get_keywords(headline), link))

# INVESTING.COM
request = Request('https://www.investing.com/news/', headers={"User-Agent": "Mozilla/5.0"})
html = urlopen(request).read()
soup = BeautifulSoup(html, "html.parser")
headlines_and_links = [(title.get_text(), "https://www.investing.com" + title['href']) for title in
                       soup.find_all("a", class_="title")]
for headline, link in headlines_and_links:
    cursor.execute(query, ("Investing.com", clean(headline).strip(), get_keywords(headline), link))

# CNN BUSINESS
html = requests.get('https://edition.cnn.com/business')
soup = BeautifulSoup(html.text, "html.parser")
headlines_and_links = [(title.get_text(), "https://edition.cnn.com/business" + title.parent['href']) for title in
                       soup.find_all("span", class_="cd__headline-text")]
for headline, link in headlines_and_links:
    cursor.execute(query, ("CNN Business", clean(headline).strip(), get_keywords(headline), link))

# REMOVE DUPLICATES AND OLDER ENTRIES
older_date = datetime.utcnow() - timedelta(days=2)
cursor.execute("DELETE FROM headlines WHERE fetched_on < %s;", (older_date,))
cursor.execute("DELETE FROM headlines original USING headlines copy WHERE original.ctid < copy.ctid "
               "AND original.headline = copy.headline;")
cursor.execute("DELETE FROM keywords;")
cursor.execute("DELETE FROM topics;")
connection.commit()

# FETCH DATA
timeframe = datetime.utcnow() - timedelta(hours=3)
cursor.execute('SELECT keywords FROM headlines WHERE fetched_on >= %s ;', (timeframe,))
raw_keywords = [keywords_array[0] for keywords_array in cursor.fetchall()]

ignore_words = ['fargo', 'opinion', 'big', 'could', 'biggest', 'month', 'making', 'street', 'moves', 'good', 'kong',
                'morgan',
                'say', 'may', 'keep', 'jump', 'new', 'one', 'people', 'time', 'since', 'million', 'year', 'back']

relevant_keywords = [word for headline in raw_keywords for word in headline if word not in ignore_words]
keywords_by_frequency = collections.Counter(relevant_keywords).most_common(15)


# LINEAR CONVERSION TO BUBBLE RADIUS
def linear_conversion(value, max, min, max_bubble_size=160, min_bubble_size=45):
    return ((value - min) * (max_bubble_size - min_bubble_size) / (max - min)) + min_bubble_size


# SET MOST COMMON WITH SCALED FREQUENCY AND ARTICLES ARRAY
max = keywords_by_frequency[0][1]
min = keywords_by_frequency[-1][1]
for keyword, frequency in keywords_by_frequency:
    cursor.execute("INSERT INTO keywords (KEYWORD, FREQUENCY) VALUES (%s,%s);",
                   (keyword, linear_conversion(frequency, max, min)))


# GET KEYWORDS ARRAY FOR EACH TOPIC
def get_keywords_by_topic(topic):
    cursor.execute("SELECT keywords FROM headlines WHERE %s=ANY(keywords) AND fetched_on >= %s;", (topic, timeframe))
    return [keywords_array[0] for keywords_array in cursor.fetchall()]

# SET UP TOPICS WITH FREQUENCY AND ARTICLES FOR EACH TOPIC KEYWORD
for topic, frequency in keywords_by_frequency[:3]:
    raw_topic_keywords = get_keywords_by_topic(topic)
    relevant_topic_keywords = [word for headline in raw_topic_keywords for word in headline if word not in ignore_words]
    topic_keywords_by_frequency = [(keyword, frequency) for keyword, frequency in
                                   collections.Counter(relevant_topic_keywords).most_common(10) if frequency > 6]
    max = topic_keywords_by_frequency[0][1]
    min = topic_keywords_by_frequency[-1][1]
    for keyword, keyword_frequency in topic_keywords_by_frequency[1:]:
        cursor.execute("INSERT INTO topics (TOPIC, KEYWORD, FREQUENCY) VALUES (%s,%s,%s);",
                       (topic, keyword, linear_conversion(keyword_frequency, max, min)))
connection.commit()

cursor.close()
connection.close()