from rest_framework import serializers
from finder.models import Database

class DatabaseOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Database
        fields = ('name', 'description', 'category', 'owner', 'author', 'tags')