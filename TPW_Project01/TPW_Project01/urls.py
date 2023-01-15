"""TPW_Project01 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from app import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.home, name="home"),
    path("<int:_id>/", views.home_categoria, name="home_categoria"),

    path("logout/", views.logout, name="logout"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    path("profile/", views.profile, name="profile"),
    path("profile/<str:username>/", views.profileUtilizador, name="profileUtilizador"),
    path("profile/<str:username>/edit", views.editProfile, name="editProfile"),
    path("profile/<str:username>/followers", views.listFollower, name="listFollower"),
    path("profile/<str:username>/following", views.listFollowing, name="listFollowing"),

    path("postadd/", views.postadd, name="postadd"),
    path("post/<int:_id>/", views.postdetail, name="postdetail"),
    path("post/<int:_id>/delete/", views.postdelete, name="deletepost"),
    path("post/<int:_id>/edit/", views.postedit, name="edit"),
    path("like/", views.like, name="like_post"),
    path("search/", views.searchuser, name="search"),
    path("follow/", views.follow, name="follow"),
    path("result/", views.searchresult, name="searchresult"),
    path("post/<int:_id>/comment/<int:_id_comment>/delete/", views.commentdelete, name="deletecomment"),
    path("404/", views.error404, name="error404"),
    path("500/", views.error500, name="error500"),
    path("search_filter/", views.search_filter, name= "search_filter"),
    path("hashtag/<str:hashtag>/",views.hashtag_list, name="hashtag_list"),
    
    path("graphics",views.graphics,name="graphics" )



]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = 'app.views.error404'
handler500 = 'app.views.error500'