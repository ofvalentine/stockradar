from rest_framework import serializers


class HeadlineSerializer(serializers.Serializer):
    source = serializers.CharField(max_length=25)
    headline = serializers.CharField()
    keywords = serializers.ListField(serializers.CharField())
    fetched_on = serializers.DateTimeField()
    link = serializers.CharField()


class KeywordSerializer(serializers.Serializer):
    keyword = serializers.CharField(max_length=25)
    frequency = serializers.FloatField()


class TopicSerializer(serializers.Serializer):
    topic = serializers.CharField(max_length=25)
    keyword = serializers.CharField(max_length=25)
    frequency = serializers.FloatField()
    id = serializers.IntegerField()
