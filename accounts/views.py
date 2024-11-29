from django.shortcuts import render

from django.contrib import messages
from .forms import UserRegistrationForm
from .models import PlantCareGuide
from .models import PlantCareGuide, Comment
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect


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
        category = request.POST.get('category')  # Capture the category value from the form

        # Get the user ID of the current logged-in user
        user_id = request.user.id

        # Create the PlantCareGuide instance with the new category field and user ID
        PlantCareGuide.objects.create(
            title=title,
            description=description,
            author_name=author_name,
            author_image=author_image,
            category=category,
            user_id=user_id  # Assign the user ID
        )

        messages.success(request, 'Plant care guide added successfully!')
        return redirect('plant_care_guides')

    return render(request, 'plantCareGuides/index.html')

@login_required  # Ensure only logged-in users can comment
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