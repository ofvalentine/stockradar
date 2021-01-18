from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.serializers import serialize
from requests.api import head
from core.models import Headline, Keyword, Topic

import re
import requests
from collections import Counter
from datetime import timedelta
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from textblob import Word
from urllib.request import Request, urlopen


class Command(BaseCommand):
    help = 'Updating the database.'    

    def handle(self, *args, **options):
        cutoff_date = timezone.now() - timedelta(days=1)
        Headline.objects.filter(fetched_on__lte=cutoff_date).delete()
        Keyword.objects.all().delete()
        Topic.objects.all().delete()
        self.populate_headline()
        self.populate_keyword_and_topic()


    def populate_headline(self):
        filter_words = ['fargo', 'opinion', 'big', 'could', 'biggest', 'month', 'making', 'street', 'moves', 'say',
                        'good', 'kong', 'morgan', 'say', 'may', 'keep', 'jump', 'new', 'one', 'people', 'time', 'first',
                        'since', 'million', 'year', 'back', 'stock', 'stocks', 'get', 'market', 'extra', 'share', 'shares'] 
        ignore_words = set(stopwords.words('english') + filter_words)
        plural_words = ['india', 'data']
        
        def create_or_update(source, data):
            for headline, link in data:
                headline = re.sub(r"(|\\r|\\n|\b[A-Z]+\s?\d?(:?[A-Z]+)?\b-)", '', headline.strip())
                if len(headline.split()) > 4:
                    try:                        
                        Headline.objects.update_or_create(source=source, headline=headline, keywords=extract_keywords(headline),
                                                        link=link, defaults={'fetched_on': timezone.now()})
                    except:
                        print('Failed headline:', headline)
            print('Finished updating data from', source)       

        def extract_keywords(headline):
            headline = re.sub(r"-", ' ', headline)  # space for dash
            headline = re.sub(r"\\n|\\t|(\b[A-Z]+\s?\d?(:?[A-Z]+)?\b)|'s|’s|([^A-Za-z ])", '', headline)  # remove special char.
            keywords = [word for word in headline.lower().split() if word not in ignore_words]  # remove stopwords
            keywords = [Word(word).singularize() for word in keywords if word not in plural_words]
            return keywords

        def parse_html(url):
            html = requests.get(url)
            return BeautifulSoup(html.text, "html.parser")

        html_text = parse_html('https://www.reuters.com/finance/markets')
        headlines_and_links = [(title.get_text(), "https://www.reuters.com" + title['href']) for title
                               in html_text.find_all("a", href=re.compile("article"))[1:]]
        create_or_update('Reuters', headlines_and_links)

        html_text = parse_html('https://www.wsj.com/news/markets')
        headlines_and_links = [(title.get_text(), title['href']) for title in
                               html_text.find_all("a", class_="wsj-headline-link", href=re.compile("articles"))]
        create_or_update('WSJ', headlines_and_links)

        html_text = parse_html('https://finance.yahoo.com/topic/stock-market-news')
        headlines_and_links = [(title.get_text(), "https://finance.yahoo.com" + title['href']) for title in
                               html_text.find_all("a", href=re.compile("news"))]
        create_or_update('Yahoo', headlines_and_links)

        html_text = parse_html('https://www.cnbc.com/finance/')
        headlines_and_links = [(title.get_text(), title['href']) for title in html_text.find_all("a", class_="Card-title")]
        create_or_update('CNBC', headlines_and_links)

        html_text = parse_html('https://www.marketwatch.com/')
        headlines_and_links = [(title.get_text(), title['href']) for title in
                               html_text.find_all("a", class_="link", href=re.compile("story"))]
        create_or_update('MarketWatch', headlines_and_links)

        html_text = parse_html('https://economictimes.indiatimes.com/markets')
        headlines_and_links = [(title.get_text(), "https://economictimes.indiatimes.com" + title['href']) for title in
                               html_text.find_all("a", href=re.compile("^\\/+(markets)+\\/+\\w+\\/+(news)")) if title.get_text()]
        create_or_update('India Times ET', headlines_and_links)

        html_text = parse_html('https://www.ft.com/markets')
        headlines_and_links = [(title.get_text(), "https://www.ft.com" + title['href']) for title in
                               html_text.find_all("a", attrs={'data-trackable': "heading-link"})]
        create_or_update('FT', headlines_and_links)

        html_text = parse_html('https://www.fnlondon.com/')
        headlines_and_links = [(title.get_text(), title['href']) for title in
                               html_text.find_all("a", class_=re.compile("FinancialNewsTheme--headline-link--"))]
        create_or_update('FN London', headlines_and_links)
        
        html_text = parse_html('https://edition.cnn.com/business')
        headlines_and_links = [(title.get_text(), "https://edition.cnn.com/business" + title.parent['href']) for title in
                               html_text.find_all("span", class_="cd__headline-text")]
        create_or_update('CNN Business', headlines_and_links)

        request = Request('https://www.investing.com/news/', headers={"User-Agent": "Mozilla/5.0"})
        html = urlopen(request).read()
        html_text = BeautifulSoup(html, "html.parser")
        headlines_and_links = [(title.get_text(), "https://www.investing.com" + title['href']) for title in
                               html_text.find_all("a", class_="title")]
        create_or_update('Investing.com', headlines_and_links)


    def populate_keyword_and_topic(self):        
        num_bubbles = 15
        num_topics = 3
        num_articles = 6
        max_bubble_size = 145
        min_bubble_size = 45
        
        def get_bubble_radius(value):
            return ((value-min_frequency) * (max_bubble_size-min_bubble_size) / (max_frequency-min_frequency)) + min_bubble_size
        
        def get_articles(keywords):
            return list(Headline.objects.filter(keywords__contains=keywords).values('source', 'headline', 'keywords', 'link')
                        .order_by('fetched_on')[:num_articles])
        
        raw_keywords = Headline.objects.all().values_list('keywords', flat=True)                 
        keywords = [word for headline in raw_keywords for word in headline]
        keywords_by_frequency = Counter(keywords).most_common(num_bubbles)        
        max_frequency = keywords_by_frequency[0][1]
        min_frequency = keywords_by_frequency[-1][1]
        Keyword.objects.bulk_create([Keyword(keyword=keyword, frequency=get_bubble_radius(frequency), articles=get_articles([keyword]))
                                     for keyword, frequency in keywords_by_frequency])
            
        topics = [keyword for keyword, _ in keywords_by_frequency[:num_topics]]
        for topic in topics:
            raw_topic_keywords = Headline.objects.filter(keywords__contains=[topic]).values_list('keywords', flat=True)            
            topic_keywords = [word for headline in raw_topic_keywords for word in headline]
            topic_keywords_by_frequency = Counter(topic_keywords).most_common(num_bubbles)
            max_frequency = topic_keywords_by_frequency[0][1]
            min_frequency = topic_keywords_by_frequency[-1][1]
            topic_data = [{'keyword': keyword, 'frequency': get_bubble_radius(frequency), 'articles': get_articles([topic, keyword])} 
                          for keyword, frequency in topic_keywords_by_frequency[1:]]
            Topic.objects.create(topic=topic, data=topic_data)