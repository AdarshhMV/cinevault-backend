from django.db import models

# Create your models here.
from django.db import models

class Movie(models.Model):
    # We will store the movie title
    title = models.CharField(max_length=255)
    
    # We store the poster URL so we can show it again later
    poster_url = models.CharField(max_length=500)
    
    # The 3 features you built in React:
    on_watchlist = models.BooleanField(default=False)
    is_watched = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.title
    
from django.db import models
from django.contrib.auth.models import User # ⬅️ Import the User model

class Movie(models.Model):
    # 🔑 NEW: Link this specific movie row to a specific User
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movies')
    
    title = models.CharField(max_length=255)
    poster_url = models.CharField(max_length=500)
    on_watchlist = models.BooleanField(default=False)
    is_watched = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movies')
    title = models.CharField(max_length=255)
    poster_url = models.CharField(max_length=500)
    genre = models.CharField(max_length=100, default="Unknown") # ⬅️ NEW FIELD
    on_watchlist = models.BooleanField(default=False)
    is_watched = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.title}"