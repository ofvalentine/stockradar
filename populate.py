# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import re
import psycopg2
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import requests
from textblob import Word
from urllib.request import Request, urlopen
import os

# CONNECT TO DATABASE
connection = psycopg2.connect(user=os.environ.get('USER'),
                              password=os.environ.get('PASSWORD'),
                              host=os.environ.get('HOST'), port="5432",
                              database=os.environ.get('DATABASE'))
cursor = connection.cursor()
query = "INSERT INTO headlines (SOURCE, HEADLINE, KEYWORDS, FETCHED_ON, LINK) VALUES (%s,%s,%s,%s,%s)"
fetched_on = datetime.utcnow()

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


# SCRAPE REUTERS MARKETS
html = requests.get('https://www.reuters.com/finance/markets')
soup = BeautifulSoup(html.text, "html.parser")
headlines_and_links = [(title.get_text(), "https://www.reuters.com" + title['href']) for title in
                       soup.find_all("a", href=re.compile("article"))[1:]]

# INSERT REUTERS HEADLINES TO DATABASE
for headline, link in headlines_and_links:
    cursor.execute(query, ("Reuters", clean(headline.strip()), get_keywords(headline), fetched_on, link))
connection.commit()

# SCRAPE WSJ MARKETS
html = requests.get('https://www.wsj.com/news/markets')
soup = BeautifulSoup(html.text, "html.parser")
headlines_and_links = [(title.get_text(), title['href']) for title in
                       soup.find_all("a", class_="wsj-headline-link", href=re.compile("articles"))]

# INSERT WSJ HEADLINES TO DATABASE
for headline, link in headlines_and_links:
    cursor.execute(query, ("WSJ", clean(headline.strip()), get_keywords(headline), fetched_on, link))
connection.commit()

# SCRAPE YAHOO FINANCE
html = requests.get('https://finance.yahoo.com/topic/stock-market-news')
soup = BeautifulSoup(html.text, "html.parser")
headlines_and_links = [(title.get_text(), "https://finance.yahoo.com" + title['href']) for title in
                       soup.find_all("a", href=re.compile("news"))]

# INSERT YAHOO HEADLINES TO DATABASE
for headline, link in headlines_and_links:
    cursor.execute(query, ("Yahoo", clean(headline.strip()), get_keywords(headline), fetched_on, link))
connection.commit()

# SCRAPE CNBC FINANCE
html = requests.get('https://www.cnbc.com/finance/')
soup = BeautifulSoup(html.text, "html.parser")
headlines_and_links = [(title.get_text(), title['href']) for title in
                       soup.find_all("a", class_="Card-title")]

# INSERT CNBC HEADLINES TO DATABASE
for headline, link in headlines_and_links:
    cursor.execute(query, ("CNBC", clean(headline.strip()), get_keywords(headline), fetched_on, link))
connection.commit()

# SCRAPE MARKETWATCH
html = requests.get('https://www.marketwatch.com/')
soup = BeautifulSoup(html.text, "html.parser")
headlines_and_links = [(title.get_text(), title['href']) for title in
                       soup.find_all("a", class_="link", href=re.compile("story"))]

# INSERT MARKETWATCH HEADLINES TO DATABASE
for headline, link in headlines_and_links:
    cursor.execute(query, ("MarketWatch", clean(headline).strip(), get_keywords(headline), fetched_on, link))
connection.commit()

# SCRAPE INDIA TIMES ET
html = requests.get('https://economictimes.indiatimes.com/markets')
soup = BeautifulSoup(html.text, "html.parser")
headlines_and_links = [(title.get_text(), "https://economictimes.indiatimes.com" + title['href']) for title in
                       soup.find_all("a", href=re.compile("^\\/+(markets)+\\/+\\w+\\/+(news)"))]

# INSERT INDIA TIMES ET HEADLINES TO DATABASE
for headline, link in headlines_and_links:
    if headline:
        cursor.execute(query, ("India Times ET", clean(headline).strip(), get_keywords(headline), fetched_on, link))
connection.commit()

# SCRAPE FINANCIAL TIMES
html = requests.get('https://www.ft.com/markets')
soup = BeautifulSoup(html.text, "html.parser")
headlines_and_links = [(title.get_text(), "https://www.ft.com" + title['href']) for title in
                       soup.find_all("a", attrs={'data-trackable': "heading-link"})]

# INSERT FINANCIAL TIMES HEADLINES TO DATABASE
for headline, link in headlines_and_links:
    cursor.execute(query, ("FT", clean(headline).strip(), get_keywords(headline), fetched_on, link))
connection.commit()

# SCRAPE FINANCIAL NEWS LONDON
html = requests.get('https://www.fnlondon.com/')
soup = BeautifulSoup(html.text, "html.parser")
headlines_and_links = [(title.get_text(), title['href']) for title in
                       soup.find_all("a", class_=re.compile("FinancialNewsTheme--headline-link--"))]

# INSERT FINANCIAL NEWS LONDON HEADLINES TO DATABASE
for headline, link in headlines_and_links:
    cursor.execute(query, ("FN London", clean(headline).strip(), get_keywords(headline), fetched_on, link))
connection.commit()

# SCRAPE INVESTING.COM
request = Request('https://www.investing.com/news/', headers={"User-Agent": "Mozilla/5.0"})
html = urlopen(request).read()
soup = BeautifulSoup(html, "html.parser")
headlines_and_links = [(title.get_text(), "https://www.investing.com" + title['href']) for title in
                       soup.find_all("a", class_="title")]

# INSERT INVESTING.COM HEADLINES TO DATABASE
for headline, link in headlines_and_links:
    cursor.execute(query, ("Investing.com", clean(headline).strip(), get_keywords(headline), fetched_on, link))
connection.commit()

# SCRAPE CNN BUSINESS
html = requests.get('https://edition.cnn.com/business')
soup = BeautifulSoup(html.text, "html.parser")
headlines_and_links = [(title.get_text(), "https://edition.cnn.com/business" + title.parent['href']) for title in
                       soup.find_all("span", class_="cd__headline-text")]

# INSERT CNN BUSINESS HEADLINES TO DATABASE
for headline, link in headlines_and_links:
    cursor.execute(query, ("CNN Business", clean(headline).strip(), get_keywords(headline), fetched_on, link))
connection.commit()

# REMOVE DUPLICATES AND OLDER ENTRIES
older_date = fetched_on - timedelta(days=2)
cursor.execute("DELETE FROM headlines original USING headlines copy WHERE original.ctid < copy.ctid "
               "AND original.headline = copy.headline;")
connection.commit()
