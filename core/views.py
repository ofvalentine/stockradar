from django.shortcuts import render
from .models import Keyword, Topic


def index(request):
    keywords = list(Keyword.objects.all().values())
    topics = list(Topic.objects.all().values())
    context = {'keywords': keywords, 'topics': topics}
    return render(request, 'bubbles.html', context=context)


