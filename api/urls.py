from django.urls import path
from . import views

urlpatterns = [
    path('save-movie/', views.save_movie, name='save_movie'),
    path('my-movies/', views.get_movies, name='get_movies'), # ⬅️ NEW PATH
    path('register/', views.register_user, name='register_user'),
    path('recommendations/', views.recommend_movies, name='recommend_movies')
]