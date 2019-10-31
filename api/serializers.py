from rest_framework import serializers


class ArticleSerializer(serializers.Serializer):
    source = serializers.CharField(max_length=25)
    headline = serializers.CharField()
    keywords = serializers.ListField(serializers.CharField())
    fetched_on = serializers.DateTimeField()
    link = serializers.CharField()


class KeywordsSerializer(serializers.Serializer):
    keywords = serializers.ListField(serializers.CharField())

    def update(self, instance, validated_data):
        instance.keywords = validated_data.get('keywords', instance.keywords)
        instance.save()
        return instance

# class MostCommonSerializer(serializers.Serializer):
#     keyword = serializers.ListField(serializers.CharField())
#     frequency = serializers.FloatField()
#     article_by_keyword = serializers.ListField(child=serializers.URLField())
