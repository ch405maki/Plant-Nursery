from django.shortcuts import render
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import PlantCareGuide, Comment
from .models import Story, Heart
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import StoryComment
from django.contrib.auth.models import User
from .forms import StoryCommentForm


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def landing_page(request):
    return render(request, 'landingPage/index.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard/index.html')

def plant_care_guides(request):
    guides = PlantCareGuide.objects.all()
    return render(request, 'plantCareGuides/index.html', {'guides': guides})

@login_required  # Ensure that the user is logged in
def add_plant_guide(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        author_name = request.POST.get('author_name')
        author_image = request.FILES.get('author_image')
        category = request.POST.get('category') 

        user_id = request.user.id

        PlantCareGuide.objects.create(
            title=title,
            description=description,
            author_name=author_name,
            author_image=author_image,
            category=category,
            user_id=user_id 
        )

        messages.success(request, 'Plant care guide added successfully!')
        return redirect('plant_care_guides')

    return render(request, 'plantCareGuides/index.html')

@login_required
def guide_detail(request, guide_id):
    
    # Fetch the specific guide by ID
    guide = get_object_or_404(PlantCareGuide, id=guide_id)
    
    # Retrieve all comments associated with the guide
    comments = guide.comments.all()
    
    if request.method == "POST":
        # Get the comment content from the form
        content = request.POST.get('content')
        
        if content:
            # Create and save the new comment
            Comment.objects.create(
                guide=guide,         # Associate the comment with the guide
                user=request.user,   # Associate the comment with the logged-in user
                content=content      # Save the comment content
            )
            # Redirect back to the same page after saving the comment
            return redirect('guide_detail', guide_id=guide.id)
    
    # Render the guide detail template, including comments
    return render(request, 'plantCareGuides/view.html', {
        'guide': guide,
        'comments': comments
    })

@login_required
def stories(request):
    stories = Story.objects.all()

    # Add `user_has_liked` attribute for each story
    if request.user.is_authenticated:  # Ensure the user is logged in
        for story in stories:
            story.user_has_liked = story.hearts.filter(user=request.user).exists()
    else:
        for story in stories:
            story.user_has_liked = False  # Not logged-in users cannot like

    return render(request, 'stories/index.html', {'stories': stories})

def add_story(request):
    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']
        image = request.FILES.get('image')
        Story.objects.create(author=request.user, title=title, content=content, image=image)
        return redirect('stories')
    
@login_required
def toggle_heart(request, story_id):
    story = get_object_or_404(Story, id=story_id)

    # Check if the user has already liked the story
    heart, created = Heart.objects.get_or_create(user=request.user, story=story)
    if not created:
        heart.delete()  # Remove the like if it already exists

    return redirect('stories')

def view_story(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    comments = story.comments.all()  # Use the related_name 'comments'

    return render(request, 'stories/view.html', {
        'story': story,
        'comments': comments
    })

def add_comment(request, story_id):
    story = get_object_or_404(Story, id=story_id)

    if request.method == 'POST':
        form = StoryCommentForm(request.POST)
        if form.is_valid():
            # Create the comment and associate it with the user and story
            StoryComment.objects.create(
                story=story,
                user=request.user,
                content=form.cleaned_data['content']
            )
            return redirect('view_story', story_id=story.id)  # Redirect to the story detail page
    else:
        form = StoryCommentForm()

    return render(request, 'story/view_story.html', {'story': story, 'form': form})