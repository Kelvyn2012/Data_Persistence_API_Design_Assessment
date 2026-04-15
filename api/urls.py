from django.urls import path
from .views import ProfileView, ProfileDetailView

urlpatterns = [
    path('profiles', ProfileView.as_view(), name='profiles'),
    path('profiles/<uuid:id>', ProfileDetailView.as_view(), name='profile-detail'),
]