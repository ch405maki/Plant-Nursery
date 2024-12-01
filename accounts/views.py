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
from .forms import ProfileUpdateForm, UserUpdateForm
from django.db import transaction
from .models import Profile
from django.urls import reverse


@login_required
def edit_profile(request):
    user = request.user

    # Ensure the user has a profile
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():  # Ensure atomic save
                user_form.save()
                profile_form.save()
            messages.success(request, "Your profile was successfully updated!")
            return redirect("dashboard")  # Redirect to the dashboard or any page

    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, "accounts/edit_profile.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })

@login_required
def profile(request):
    """
    View to display the user's profile information.
    """
    user_profile = Profile.objects.get(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': user_profile})

@login_required
def profile_view(request):
    profile = request.user.profile
    return render(request, "accounts/profile.html", {"profile": profile})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            # Check if the user already has a profile
            if not hasattr(user, 'profile'):
                # Create a profile if it doesn't exist
                Profile.objects.create(user=user)

            # Redirect to a success page or login
            return redirect('login')  # Redirect to the login page, or another page you prefer
        else:
            # Handle form errors
            pass

    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

def landing_page(request):
    return render(request, 'landingPage/index.html')

@login_required
def dashboard(request):
    user = request.user

    # Aggregate data
    total_guides = PlantCareGuide.objects.filter(user=user).count()
    total_drafts = PlantCareGuide.objects.filter(user=user, is_draft=True).count()
    total_hearts = HeartGuide.objects.filter(guide__user=user).count()

    # Recent guides - you can filter this by category if you want to display only specific categories
    recent_guides = PlantCareGuide.objects.filter(user=user).order_by('-created_at')[:5]

    # Add the counts per category
    total_plant_care_guides = PlantCareGuide.objects.filter(user=user, category="Plant Care Guides").count()
    total_gardening_tips = PlantCareGuide.objects.filter(user=user, category="Gardening Tips").count()
    total_design_inspirations = PlantCareGuide.objects.filter(user=user, category="Design Inspirations").count()
    total_qa_guides = PlantCareGuide.objects.filter(user=user, category="Plant Q&A").count()

    context = {
        'total_guides': total_guides,
        'total_drafts': total_drafts,
        'total_hearts': total_hearts,
        'recent_guides': recent_guides,
        'total_plant_care_guides': total_plant_care_guides,
        'total_gardening_tips': total_gardening_tips,
        'total_design_inspirations': total_design_inspirations,
        'total_qa_guides': total_qa_guides,
    }

    return render(request, 'dashboard/index.html', context)


def plant_care_guides(request):
    # Get the category from the query parameter
    category = request.GET.get('category', None)
    
    guides = PlantCareGuide.objects.filter(is_draft=False)

    if category:
        guides = guides.filter(category=category)

    if request.user.is_authenticated:
        user_hearts = HeartGuide.objects.filter(guide=OuterRef('pk'), user=request.user)
        guides = guides.annotate(user_has_liked=Exists(user_hearts))

    return render(request, 'plantCareGuides/index.html', {'guides': guides, 'category': category})


@login_required
def uploaded_plant_care_guides(request):
    # Fetch guides with category = "Plant Care Guides" and precomputed heart counts
    guides = PlantCareGuide.objects.filter(user=request.user, category="Plant Care Guides").annotate(hearts_count=Count('hearts'))
    return render(request, "uploaded/index.html", {"guides": guides})

@login_required
def uploaded_gardening_tips(request):
    # Fetch guides with category = "Gardening Tips" and precomputed heart counts
    guides = PlantCareGuide.objects.filter(user=request.user, category="Gardening Tips").annotate(hearts_count=Count('hearts'))
    return render(request, "uploaded/index.html", {"guides": guides})

@login_required
def uploaded_design_inspirations(request):
    # Fetch guides with category = "Design Inspirations" and precomputed heart counts
    guides = PlantCareGuide.objects.filter(user=request.user, category="Design Inspirations").annotate(hearts_count=Count('hearts'))
    return render(request, "uploaded/index.html", {"guides": guides})

@login_required
def uploaded_qa(request):
    # Fetch guides with category = "Design Inspirations" and precomputed heart counts
    guides = PlantCareGuide.objects.filter(user=request.user, category="Plant QA").annotate(hearts_count=Count('hearts'))
    return render(request, "uploaded/index.html", {"guides": guides})

@login_required
def update_draft(request, draft_id):
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
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        author_name = request.POST.get('author_name')
        author_image = request.FILES.get('author_image')
        category = request.POST.get('category')
        is_draft = request.POST.get('is_draft') == 'True'

        # Create the guide
        guide = PlantCareGuide.objects.create(
            title=title,
            description=description,
            author_name=author_name,
            author_image=author_image,
            category=category,
            user=request.user,
            is_draft=is_draft
        )

        # Redirect back to the category index
        return redirect(f"{reverse('plant_care_guides')}?category={category}")

    return redirect(f"{reverse('plant_care_guides')}?category={category}")

@login_required
def saved_drafts(request):
    drafts = PlantCareGuide.objects.filter(user=request.user, is_draft=True)
    return render(request, 'plantCareGuides/drafts.html', {'drafts': drafts})


@login_required
def guide_detail(request, guide_id):
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
    guide = get_object_or_404(PlantCareGuide, id=guide_id)
    heart, created = HeartGuide.objects.get_or_create(guide=guide, user=request.user)

    if not created:
        heart.delete()

    # Redirect back to the index page
    return redirect('plant_care_guides')

@login_required
def toggle_save_guide(request, guide_id):
    guide = get_object_or_404(PlantCareGuide, id=guide_id)
    saved_guide, created = SavedGuide.objects.get_or_create(guide=guide, user=request.user)

    if not created:
        saved_guide.delete()

    return redirect('plant_care_guides')  # Redirect to the guides list or to the saved guides page

@login_required
def saved_guides(request):
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
def uploaded_stories(request):
    # Fetch all stories uploaded by the logged-in user (using 'author' to filter)
    stories = Story.objects.filter(author=request.user)
    print(stories)  # Check if the correct stories are being fetched
    return render(request, "uploaded/stories/index.html", {"stories": stories})

  
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