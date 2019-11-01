from django.shortcuts import render
from .models import Headline, Keyword
from .serializers import KeywordSerializer


def index(request):
    keywords = Keyword.objects.filter()
    keywords_serializer = KeywordSerializer(keywords, many=True)
    print(keywords_serializer)
    return render(request, 'index.html')
