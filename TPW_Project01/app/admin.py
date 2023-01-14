from django.contrib import admin
from app.models import Profile, Follow, Hashtag, Post, Comment



# Register your models here.
admin.site.register(Profile)
admin.site.register(Follow)
admin.site.register(Hashtag)
admin.site.register(Post)
admin.site.register(Comment)
