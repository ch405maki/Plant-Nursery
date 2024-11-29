from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('plant-care-guides/', views.plant_care_guides, name='plant_care_guides'),
    path('add-plant-guide/', views.add_plant_guide, name='add_plant_guide'),
    path('view/<int:guide_id>/', views.guide_detail, name='guide_detail'),  

    path('stories/', views.stories, name='stories'),  
    path('add-story/', views.add_story, name='add_story'),
]
