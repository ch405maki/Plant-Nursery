from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('plant-care-guides/', views.plant_care_guides, name='plant_care_guides'),
    
    path('add-plant-guide/', views.add_plant_guide, name='add_plant_guide'),
    path('view/<int:guide_id>/', views.guide_detail, name='guide_detail'),  
    path('guides/<int:guide_id>/toggle_heart/', views.toggle_heart_guide, name='toggle_heart_guide'),
    path('guides/<int:guide_id>/toggle_save/', views.toggle_save_guide, name='toggle_save_guide'),
    path('saved/', views.saved_guides, name='saved'),
    path('drafts/', views.saved_drafts, name='drafts'),
    path('drafts/<int:draft_id>/update/', views.update_draft, name='update_draft'),


    path('stories/', views.stories, name='stories'),  
    path('add-story/', views.add_story, name='add_story'),
    path('story/<int:story_id>/heart/', views.toggle_heart, name='toggle_heart'),
    path('story/<int:story_id>/view/', views.view_story, name='view_story'),
    path('story/<int:story_id>/add_comment/', views.add_comment, name='add_comment'),

    path('uploaded/plant-care-guides/', views.uploaded_plant_care_guides, name='uploaded_plant_care_guides'),
    path('uploaded/gardening-tips/', views.uploaded_gardening_tips, name='uploaded_gardening_tips'),
    path('uploaded/design-inspirations/', views.uploaded_design_inspirations, name='uploaded_design_inspirations'),
    path('uploaded/qa/', views.uploaded_design_inspirations, name='uploaded_qa'),
    path('uploaded/stories/', views.uploaded_stories, name='uploaded_stories'),

]
