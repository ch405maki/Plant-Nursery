from django.shortcuts import render
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import Story, Heart
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import StoryComment
from django.contrib.auth.models import User
from .forms import StoryCommentForm
from .models import PlantCareGuide, HeartGuide, Comment, SavedGuide
from django.db.models import Exists, OuterRef



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
    """
    View for displaying all plant care guides, excluding drafts and including
    whether the logged-in user has liked each guide.
    """
    # Filter out drafts by ensuring only guides where is_draft is False are shown
    guides = PlantCareGuide.objects.filter(is_draft=False)

    if request.user.is_authenticated:
        # Annotate whether the current user has liked each guide
        user_hearts = HeartGuide.objects.filter(guide=OuterRef('pk'), user=request.user)
        guides = guides.annotate(user_has_liked=Exists(user_hearts))

    return render(request, 'plantCareGuides/index.html', {'guides': guides})

@login_required
def update_draft(request, draft_id):
    """
    View to update a saved draft and optionally publish it as a guide.
    """
    draft = get_object_or_404(PlantCareGuide, id=draft_id, user=request.user, is_draft=True)

    if request.method == "POST":
        # Update the fields based on form data
        draft.title = request.POST.get("title")
        draft.description = request.POST.get("description")
        draft.author_name = request.POST.get("author_name")
        draft.category = request.POST.get("category")
        draft.is_draft = False
        
        # Handle author image upload
        if "author_image" in request.FILES:
            draft.author_image = request.FILES["author_image"]
        
        draft.save()

        # Redirect based on action
        if not draft.is_draft:
            return redirect("plant_care_guides")  # Redirect to guides page
        return redirect("drafts")  # Redirect to drafts page

    return render(request, "plantCareGuides/update_draft.html", {"draft": draft})


@login_required
def add_plant_guide(request):
    """
    View to handle adding a new plant care guide. Includes functionality for saving drafts.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        author_name = request.POST.get('author_name')
        author_image = request.FILES.get('author_image')
        category = request.POST.get('category')
        is_draft = request.POST.get('is_draft') == 'True'  # Get the draft status

        # Save the guide to the database
        guide = PlantCareGuide.objects.create(
            title=title,
            description=description,
            author_name=author_name,
            author_image=author_image,
            category=category,
            user=request.user,
            is_draft=is_draft
        )

        # Redirect to a page after saving the guide (could be saved drafts page or success page)
        return redirect('plant_care_guides')

    return render(request, 'add_plant_guide.html')

@login_required
def saved_drafts(request):
    """
    View to show all drafts for the logged-in user.
    """
    drafts = PlantCareGuide.objects.filter(user=request.user, is_draft=True)
    return render(request, 'plantCareGuides/drafts.html', {'drafts': drafts})


@login_required
def guide_detail(request, guide_id):
    """
    View for displaying a single guide and its comments.
    Allows posting new comments.
    """
    guide = get_object_or_404(PlantCareGuide, id=guide_id)
    comments = guide.comments.all()

    # Check if the user has liked the guide
    user_has_liked = guide.hearts.filter(user=request.user).exists()

    if request.method == "POST":
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                guide=guide,
                user=request.user,
                content=content
            )
            messages.success(request, "Your comment has been added!")
            return redirect('guide_detail', guide_id=guide.id)

    return render(request, 'plantCareGuides/view.html', {
        'guide': guide,
        'comments': comments,
        'user_has_liked': user_has_liked
    })


@login_required
def toggle_heart_guide(request, guide_id):
    """
    View to toggle (add/remove) a heart for a guide by the logged-in user.
    """
    guide = get_object_or_404(PlantCareGuide, id=guide_id)
    heart, created = HeartGuide.objects.get_or_create(guide=guide, user=request.user)

    if not created:
        heart.delete()

    # Redirect back to the index page
    return redirect('plant_care_guides')

@login_required
def toggle_save_guide(request, guide_id):
    """
    View to toggle (add/remove) a saved guide for the logged-in user.
    """
    guide = get_object_or_404(PlantCareGuide, id=guide_id)
    saved_guide, created = SavedGuide.objects.get_or_create(guide=guide, user=request.user)

    if not created:
        saved_guide.delete()

    return redirect('plant_care_guides')  # Redirect to the guides list or to the saved guides page

@login_required
def saved_guides(request):
    """
    View to show all saved guides for the logged-in user.
    """
    saved_guides = SavedGuide.objects.filter(user=request.user)
    return render(request, 'plantCareGuides/saved.html', {'saved_guides': saved_guides})


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