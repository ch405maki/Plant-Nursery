from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import PlantCareGuide


from django.contrib.auth.decorators import login_required

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
    return render(request, 'accounts/landing_page.html')

@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

def plant_care_guides(request):
    guides = PlantCareGuide.objects.all()
    return render(request, 'plantCareGuides/index.html', {'guides': guides})

def add_plant_guide(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        author_name = request.POST.get('author_name')
        author_image = request.FILES.get('author_image')

        PlantCareGuide.objects.create(
            title=title,
            description=description,
            author_name=author_name,
            author_image=author_image
        )

        messages.success(request, 'Plant care guide added successfully!')
        return redirect('plant_care_guides')

    return render(request, 'plantCareGuides/index.html')

