from django.contrib.auth.models import User
from django.db import models

class PlantCareGuide(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    author_name = models.CharField(max_length=100)
    author_image = models.ImageField(upload_to='author_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title