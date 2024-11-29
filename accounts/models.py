from django.contrib.auth.models import User
from django.db import models

class PlantCareGuide(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    author_name = models.CharField(max_length=100)
    author_image = models.ImageField(upload_to='author_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    category = models.CharField(max_length=100, default='Uncategorized')

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    guide = models.ForeignKey('PlantCareGuide', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.guide.title}"

class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stories")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='stories_images/', blank=True, null=True)  # Image field

    def __str__(self):
        return self.title
    @property
    def hearts_count(self):
        return self.hearts.count()
    
class Heart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hearts")
    story = models.ForeignKey('Story', on_delete=models.CASCADE, related_name="hearts")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'story')  # Ensure a user can like a story only once

    def __str__(self):
        return f"{self.user.username} liked {self.story.title}"

class StoryComment(models.Model):
    story = models.ForeignKey(Story, related_name='comments', on_delete=models.CASCADE)  # Link to Story
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User
    content = models.TextField()  # The actual content of the comment
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of when the comment was created

    class Meta:
        db_table = 'story_comment'  # Custom table name

    def __str__(self):
        return f"{self.user.username} commented on {self.story.title}"
