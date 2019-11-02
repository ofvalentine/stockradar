from django.shortcuts import render
from .models import Headline, Keyword, Topic
from django.utils import timezone
from datetime import timedelta


def index(request):
    keywords = list(Keyword.objects.all().values())
    timeframe = timezone.now() - timedelta(hours=3)
    for keyword_dict in keywords:
        keyword_dict['articles'] = list(Headline.objects.filter(fetched_on__gte=timeframe, keywords__contains=[
            keyword_dict['keyword']]).values('source', 'headline', 'keywords', 'link').order_by('fetched_on')[:6])
    topics = list(Topic.objects.distinct('topic').values('topic'))
    for topic_dict in topics:
        topic_keywords = list(Topic.objects.filter(topic=topic_dict['topic']).values('keyword', 'frequency'))
        for keyword_dict in topic_keywords:
            keyword_dict['articles'] = list(Headline.objects.filter(fetched_on__gte=timeframe, keywords__contains=[
                            topic_dict['topic'], keyword_dict['keyword']]).values('source', 'headline', 'keywords',
                                                                                  'link').order_by('fetched_on')[:6])
        topic_dict['data'] = topic_keywords
    context = {'keywords': keywords, 'topics': topics}
    return render(request, 'bubbles.html', context=context)
