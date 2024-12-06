from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Exists, OuterRef
from django.db import transaction
from .models import PlantCareGuide, HeartGuide, Comment, SavedGuide
from .models import Story, Heart
from .models import Profile
from .models import Notification
from .forms import ProfileUpdateForm, UserUpdateForm
from .forms import StoryCommentForm
from .forms import StoryComment
from .forms import UserRegistrationForm



@login_required
def edit_profile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic(): 
                user_form.save()
                profile_form.save()
            messages.success(request, "Your profile was successfully updated!")
            return redirect("dashboard") 

    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, "accounts/edit_profile.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })

@login_required
def profile(request):
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

            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user)

            return redirect('login')
        else:
            pass

    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

def landing_page(request):
    return render(request, 'landingPage/index.html')

def about(request):
    return render(request, 'about/index.html')

def contact(request):
    return render(request, 'contact/index.html')

@login_required
def dashboard(request):
    user = request.user

    total_guides = PlantCareGuide.objects.filter(user=user).count()
    total_drafts = PlantCareGuide.objects.filter(user=user, is_draft=True).count()
    total_hearts = HeartGuide.objects.filter(guide__user=user).count()

    recent_guides = PlantCareGuide.objects.filter(user=user).order_by('-created_at')[:5]

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
    guides = PlantCareGuide.objects.filter(user=request.user, category="Plant Care Guides").annotate(hearts_count=Count('hearts'))
    return render(request, "uploaded/index.html", {"guides": guides})

@login_required
def uploaded_gardening_tips(request):
    # Fetch guides with category = "Gardening Tips" and precomputed heart counts
    guides = PlantCareGuide.objects.filter(user=request.user, category="Gardening Tips").annotate(hearts_count=Count('hearts'))
    return render(request, "uploaded/index.html", {"guides": guides})

@login_required
def uploaded_design_inspirations(request):
    guides = PlantCareGuide.objects.filter(user=request.user, category="Design Inspirations").annotate(hearts_count=Count('hearts'))
    return render(request, "uploaded/index.html", {"guides": guides})

@login_required
def uploaded_qa(request):
    guides = PlantCareGuide.objects.filter(user=request.user, category="Plant QA").annotate(hearts_count=Count('hearts'))
    return render(request, "uploaded/index.html", {"guides": guides})

@login_required
def update_draft(request, draft_id):
    draft = get_object_or_404(PlantCareGuide, id=draft_id, user=request.user, is_draft=True)

    if request.method == "POST":
        draft.title = request.POST.get("title")
        draft.description = request.POST.get("description")
        draft.author_name = request.POST.get("author_name")
        draft.category = request.POST.get("category")
        draft.is_draft = False
        
        if "author_image" in request.FILES:
            draft.author_image = request.FILES["author_image"]
        
        draft.save()

        if not draft.is_draft:
            return redirect("plant_care_guides") 
        return redirect("drafts") 

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

        guide = PlantCareGuide.objects.create(
            title=title,
            description=description,
            author_name=author_name,
            author_image=author_image,
            category=category,
            user=request.user,
            is_draft=is_draft
        )

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

    user_has_liked = guide.hearts.filter(user=request.user).exists()

    if request.method == "POST":
        content = request.POST.get('content')
        if content:
            comment = Comment.objects.create(
                guide=guide,
                user=request.user,
                content=content
            )

            if comment.user != guide.user:
                Notification.objects.create(
                    user=guide.user,
                    message=f"{comment.user.username} commented on your guide: {guide.title}",
                    link=f"/accounts/view/{guide.id}/",
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

    return redirect('plant_care_guides')

@login_required
def toggle_save_guide(request, guide_id):
    guide = get_object_or_404(PlantCareGuide, id=guide_id)
    saved_guide, created = SavedGuide.objects.get_or_create(guide=guide, user=request.user)

    if not created:
        saved_guide.delete()

    return redirect('plant_care_guides') 
@login_required
def saved_guides(request):
    saved_guides = SavedGuide.objects.filter(user=request.user)
    return render(request, 'plantCareGuides/saved.html', {'saved_guides': saved_guides})


@login_required
def stories(request):
    stories = Story.objects.all()

    if request.user.is_authenticated: 
        for story in stories:
            story.user_has_liked = story.hearts.filter(user=request.user).exists()
    else:
        for story in stories:
            story.user_has_liked = False 

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
    stories = Story.objects.filter(author=request.user)
    print(stories) 
    return render(request, "uploaded/stories/index.html", {"stories": stories})

  
@login_required
def toggle_heart(request, story_id):
    story = get_object_or_404(Story, id=story_id)

    heart, created = Heart.objects.get_or_create(user=request.user, story=story)
    if not created:
        heart.delete() 

    return redirect('stories')

def view_story(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    comments = story.comments.all() 

    return render(request, 'stories/view.html', {
        'story': story,
        'comments': comments
    })

def add_comment(request, story_id):
    story = get_object_or_404(Story, id=story_id)

    if request.method == 'POST':
        form = StoryCommentForm(request.POST)
        if form.is_valid():
            StoryComment.objects.create(
                story=story,
                user=request.user,
                content=form.cleaned_data['content']
            )
            return redirect('view_story', story_id=story.id)
    else:
        form = StoryCommentForm()

    return render(request, 'story/view_story.html', {'story': story, 'form': form})

def send_comment_notification(comment):
    guide_owner = comment.guide.user
    notification_message = f"{comment.user.username} commented says: {comment.guide.title}"
    Notification.objects.create(
        user=guide_owner,
        message=notification_message,
        link=f"/accounts/view/{comment.guide.id}/",
    )

@login_required
def notifications(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    unread_notifications_count = request.user.notifications.filter(is_read=False).count()
    return render(request, 'notifications/index.html', {
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    })


@login_required
def mark_notification_as_read(request, notification_id):
    if request.method == "POST":
        notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return redirect('notifications') 
    return redirect('notifications') 

