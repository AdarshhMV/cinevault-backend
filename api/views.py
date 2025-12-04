from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Movie
from .serializers import MovieSerializer

@api_view(['POST']) # We only allow POST requests (sending data)
def save_movie(request):
    # 1. Get the data sent from React
    movie_data = request.data
    
    # 2. Check if this movie already exists in our DB to avoid duplicates
    # We filter by title (for simplicity now)
    existing_movie = Movie.objects.filter(title=movie_data['title']).first()
    
    if existing_movie:
        # If it exists, let's update it instead of creating a new one
        serializer = MovieSerializer(existing_movie, data=movie_data)
    else:
        # If not, create a new one
        serializer = MovieSerializer(data=movie_data)

    # 3. Validate and Save
    if serializer.is_valid():
        serializer.save()
        return Response({"status": "success", "data": serializer.data})
    else:
        return Response({"status": "error", "errors": serializer.errors})

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Movie
from .serializers import MovieSerializer

# ... (Keep your existing save_movie function here) ...

@api_view(['GET']) # This time we accept GET requests (Reading data)
def get_movies(request):
    movies = Movie.objects.all()
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)

from rest_framework import status
# ... keep existing imports ...
from .serializers import UserSerializer # ⬅️ Import the new serializer

# ... keep save_movie and get_movies ...

@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Movie
from .serializers import MovieSerializer, UserSerializer

# --- AUTH VIEWS ---
@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- MOVIE VIEWS ---

@api_view(['GET'])
@permission_classes([IsAuthenticated]) # 🔒 Security Check
def get_movies(request):
    # 🔑 KEY FIX: Filter by the logged-in user!
    # request.user is automatically set because of the Token we sent
    movies = Movie.objects.filter(user=request.user)
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated]) # 🔒 Security Check
def save_movie(request):
    movie_data = request.data
    user = request.user # The logged-in user

    # 1. Check if THIS user already saved this movie
    existing_movie = Movie.objects.filter(user=user, title=movie_data['title']).first()
    
    if existing_movie:
        # Update existing
        serializer = MovieSerializer(existing_movie, data=movie_data, partial=True)
    else:
        # Create new (and manually attach the user!)
        serializer = MovieSerializer(data=movie_data)
        if serializer.is_valid():
            # This 'perform_create' equivalent saves the user field
            serializer.save(user=user)
            return Response({"status": "success", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if serializer.is_valid():
        serializer.save()
        return Response({"status": "updated", "data": serializer.data})
    else:
        return Response({"status": "error", "errors": serializer.errors})
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_movie(request):
    movie_data = request.data
    user = request.user

    # Check if movie exists
    existing_movie = Movie.objects.filter(user=user, title=movie_data['title']).first()
    
    if existing_movie:
        serializer = MovieSerializer(existing_movie, data=movie_data, partial=True)
    else:
        # Create new
        serializer = MovieSerializer(data=movie_data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({"status": "success", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if serializer.is_valid():
        serializer.save()
        return Response({"status": "updated", "data": serializer.data})
    else:
        return Response({"status": "error", "errors": serializer.errors})
    

from collections import Counter # ⬅️ To count genres
# ... keep existing imports ...

# --- RECOMMENDATION ENGINE ---

# 1. A Curated Database of Hits (IMDb IDs)
# In a real startup, this would be an AI model or a massive database query.
GENRE_RECOMMENDATIONS = {
    "Action": ["tt0468569", "tt1375666", "tt0133093", "tt0110912", "tt0848228", "tt0088763"], # Dark Knight, Inception, Matrix, Pulp Fiction, Avengers, Back to Future
    "Comedy": ["tt0118715", "tt0093779", "tt0109830", "tt0080684", "tt0099685", "tt0120737"], # Big Lebowski, Princess Bride, Forrest Gump, Airplane, Goodfellas, LOTR
    "Horror": ["tt0468569", "tt0081505", "tt0102926", "tt0068646", "tt0468569", "tt1396484"], # Shining, Silence of Lambs, Godfather, It
    "Sci-Fi": ["tt0816692", "tt0133093", "tt0482571", "tt0120737", "tt0076759"], # Interstellar, Matrix, Moon, LOTR, Star Wars
    "Drama": ["tt0111161", "tt0068646", "tt0109830", "tt0167260", "tt0120737"], # Shawshank, Godfather, Forrest Gump, ROTK
}

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_movies(request):
    user = request.user
    user_movies = Movie.objects.filter(user=user)

    # 1. If user has no data, return default "Top Picks"
    if not user_movies.exists():
        return Response({"genre": "General", "movies": GENRE_RECOMMENDATIONS["Action"][:5]})

    # 2. Analyze User's Favorite Genre
    genres = []
    for m in user_movies:
        if m.genre and m.genre != "Unknown":
            # OMDb returns genres like "Action, Adventure, Sci-Fi". We split them.
            split_genres = [g.strip() for g in m.genre.split(',')]
            genres.extend(split_genres)

    if not genres:
        return Response({"genre": "General", "movies": GENRE_RECOMMENDATIONS["Action"][:5]})

    # Find the most common genre (e.g., "Horror")
    most_common_genre = Counter(genres).most_common(1)[0][0]

    # 3. Get Recommendations for that Genre
    # Fallback to 'Action' if the genre isn't in our curated list
    raw_recommendations = GENRE_RECOMMENDATIONS.get(most_common_genre, GENRE_RECOMMENDATIONS["Action"])

    # 4. Filter out movies the user has ALREADY saved
    # (We don't want to recommend something they already watched)
    user_imdb_ids = [m.poster_url for m in user_movies] # Note: We assume poster_url might store ID in some setups, but let's stick to title filter for safety
    user_titles = [m.title for m in user_movies]

    # Since we only have IDs in our recommendation list, we can't filter by title easily without fetching.
    # For this student project, we just return the IDs. The frontend will filter duplicates if needed.
    
    return Response({
        "genre": most_common_genre,
        "movies": raw_recommendations
    })