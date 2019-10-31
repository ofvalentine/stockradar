from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Headline
from .serializers import KeywordsSerializer, ArticleSerializer
from datetime import datetime, timedelta
from django.utils import timezone
import collections


ignore_words = ['fargo', 'opinion', 'big', 'could', 'biggest', 'month', 'making', 'street', 'moves', 'good', 'kong',
                'morgan', 'say', 'may', 'keep', 'jump', 'new', 'one', 'people', 'time', 'since', 'million', 'year',
                'back']


def get_keywords_by_frequency(timeframe):
    api_data = Headline.objects.filter(fetched_on__gte=timeframe).values('keywords')
    serializer = KeywordsSerializer(api_data, many=True)
    raw_keywords = [keywords_dict['keywords'] for keywords_dict in serializer.data]
    relevant_keywords = [word for headline in raw_keywords for word in headline if word not in ignore_words]
    keywords_by_frequency = collections.Counter(relevant_keywords).most_common()
    return keywords_by_frequency


def article_by_keyword(timeframe, keyword):
    api_data = Headline.objects.filter(fetched_on__gte=timeframe,
                                       keywords__contains=[keyword]).order_by('fetched_on')[:6]
    serializer = ArticleSerializer(api_data, many=True)
    return serializer.data


def linear_conversion(value, max, min, max_bubble_size=160, min_bubble_size=45):
    return ((value - min) * (max_bubble_size - min_bubble_size) / (max - min)) + min_bubble_size


class KeywordsView(APIView):
    def get(self, request):
        timeframe = timezone.now() - timedelta(hours=3)
        keywords_by_frequency = get_keywords_by_frequency(timeframe)
        keywords_to_show = 15
        most_common = {}
        max = keywords_by_frequency[0][1]
        min = keywords_by_frequency[keywords_to_show - 1][1]
        for keyword, frequency in keywords_by_frequency[:keywords_to_show]:
            most_common[keyword] = linear_conversion(frequency, max, min), article_by_keyword(timeframe, keyword)
        return Response(most_common)


def get_keywords_by_topic(timeframe, topic):
    api_data = Headline.objects.filter(fetched_on__gte=timeframe, keywords__contains=[topic]).values('keywords')
    serializer = KeywordsSerializer(api_data, many=True)
    raw_topic_keywords = [keywords_dict['keywords'] for keywords_dict in serializer.data]
    relevant_topic_keywords = [word for headline in raw_topic_keywords for word in headline if word not in ignore_words]
    return relevant_topic_keywords


def articles_by_topic(timeframe, topic, keyword):
    api_data = Headline.objects.filter(fetched_on__gte=timeframe,
                                       keywords__contains=[keyword, topic]).order_by('fetched_on')[:6]
    serializer = ArticleSerializer(api_data, many=True)
    return serializer.data


class TopicsView(APIView):
    def get(self, request):
        timeframe = timezone.now() - timedelta(hours=3)
        relevant_keywords = get_keywords_by_frequency(timeframe)
        raw_topics = [topic for topic, frequency in relevant_keywords if frequency > 10]

        minimum_frequency = 6
        topics = {}
        for topic in raw_topics:
            relevant_topic_keywords = get_keywords_by_topic(timeframe, topic)
            topic_keywords_by_frequency = collections.Counter(relevant_topic_keywords).most_common()
            max = topic_keywords_by_frequency[0][1]
            min = topic_keywords_by_frequency[-1][1]
            topics[topic] = [(keyword, linear_conversion(frequency, max, min), articles_by_topic(timeframe, topic, keyword))
                             for keyword, frequency in topic_keywords_by_frequency[1:] if frequency > minimum_frequency]
        return Response(topics)
