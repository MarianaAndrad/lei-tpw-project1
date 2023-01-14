from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True, default= 'default.png')
    bio = models.TextField('Biografia', max_length=500, blank=True)
    
    def update_image(self, file):
        self.profile_pic.storage.delete(self.profile_pic.name)
        self.profile_pic = file

    def update_password(self, password):
        self.user.password = password

    def __str__(self):
        return self.user.username


class Follow(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="profile")
    following = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="following")

    def __str__(self):
        return self.profile.user.username + " follows " + self.following.user.username

class Hashtag(models.Model):
    hashtag = models.CharField(max_length=100)

    def __str__(self):
        return self.hashtag

class Post(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    caption = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_pics', blank=True)
    likes = models.ManyToManyField(Profile, related_name='likes', blank=True, default=None)
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    hashtags = models.ManyToManyField(Hashtag, related_name='hashtags', blank=True)

    def __str__(self):
        return self.caption

    def delete(self):
        self.image.storage.delete(self.image.name)
        super().delete()
    
    def get_hashtags(self):
        return self.hashtags.all()

    def get_likes_count(self):
        return self.likes.count()
    
    def user_has_liked(self, profile):
        return self.likes.filter(id=profile.id).exists()

    def remove_like(self, profile):
        self.likes.remove(profile)    
        self.like_count -= 1
        super().save()

    def add_like(self, profile):
        self.likes.add(profile)
        self.like_count += 1
        super().save()
    
    def add_hashtag(self,hashtag):
        self.hashtags.add(hashtag)
        super().save()

    def add_comment(self):
        self.comment_count += 1
        super().save()
    
    def remove_comment(self):
        self.comment_count -= 1
        super().save()

    class Meta:
        ordering = ['-date']

class Comment(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment

    class Meta:
        ordering = ['-date']
