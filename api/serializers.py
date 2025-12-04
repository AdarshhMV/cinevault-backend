from rest_framework import serializers
from .models import Movie

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'poster_url', 'on_watchlist', 'is_watched', 'rating']

from rest_framework import serializers
from .models import Movie
from django.contrib.auth.models import User # ⬅️ Import the built-in User model

# ... (Keep your MovieSerializer here) ...
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'poster_url', 'on_watchlist', 'is_watched', 'rating']

# ⬇️ ADD THIS NEW SERIALIZER
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # This automatically hashes the password!
        user = User.objects.create_user(**validated_data)
        return user
    
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'poster_url', 'genre', 'on_watchlist', 'is_watched', 'rating'] # ⬅️ Added 'genre'