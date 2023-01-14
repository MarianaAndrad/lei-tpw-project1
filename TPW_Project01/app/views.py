from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from app.forms import FormSingup, FormLogin, CommentForm, ImageForm, PasswordForm, BioForm, EditPostForm, SearchForm
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from app.models import Profile, Post, Comment, Follow,Hashtag
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate

def home(request):
    if request.user.is_authenticated:
        ctx = {
            "friend":True,
            "posts": Post.objects.all().order_by("-date"),
            "profile": get_object_or_404(Profile, user=request.user),
            "form_search": SearchForm(),
            "exist": True
        }

        return render(request, "home.html", ctx)
    else:
        ctx={
            "friend": False,
            "posts": Post.objects.all().order_by("-date"),
            "comments_count": Comment.objects.all().count(),
            "form_search": SearchForm(),
            "exist": False
        }
        return render(request, "home.html", ctx)

# *User
def signup(request):
    if request.method == "POST":
        formSignup = FormSingup(request.POST)

        if formSignup.is_valid():

            username = formSignup.cleaned_data.get("username")
            email = formSignup.cleaned_data["email"]
            password = formSignup.cleaned_data["password"]
            confirmation = formSignup.cleaned_data["confirmation"]

            if password == confirmation:
                if User.objects.filter(username=username).exists():
                    return render(request, "signup.html", {"messages": "Username already exists." , "formSignup": formSignup})
                elif User.objects.filter(email=email).exists():
                    return render(request, "signup.html", {"messages": "Email already exists.", "formSignup": formSignup})
                elif request.FILES:
                    photo = request.FILES["photo"]
                    user = User.objects.create_user(username=username, password=password, email=email)
                    profile = Profile.objects.create(user=user, profile_pic=photo)
                    profile.save()
                    auth_login(request, User.objects.get(username=username))
                    return redirect("home")
                else:
                    user = User.objects.create_user(username=username, password=password, email=email)
                    user.save()
                    profile = Profile.objects.create(user=user)
                    profile.save()
                    auth_login(request, user)
                    return redirect("home")

            else:
                return render(request, "signup.html", {"messages": "Passwords do not match.", "formSignup": formSignup, "form_search": SearchForm()})
        else:
            return render(request, "signup.html", {"messages": "Invalid credentials.", "formSignup": formSignup, "form_search": SearchForm()})

    else:
        return render(request, "signup.html", {"formSignup": FormSingup(), "form_search": SearchForm()})

def login(request):
    if request.user.is_authenticated:
        return redirect("home") 
    else:
        if request.method == "POST":
            formLogin = FormLogin(request.POST)
            if formLogin.is_valid():
                username = formLogin.cleaned_data.get("username")
                password = formLogin.cleaned_data.get("password")
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    auth_login(request, user)
                    return redirect("home")
                else:
                    return render(request, "login.html", {"messages": "Invalid credentials.", "formLogin": formLogin, "form_search": SearchForm()})
            else:
                return render(request, "login.html", {"messages": "Invalid credentials.", "formLogin": formLogin, "form_search": SearchForm()})
        else:
            return render(request, "login.html", {"formLogin": FormLogin(), "form_search": SearchForm()})

@login_required(login_url='/login/')
def logout(request):
    auth_logout(request)
    return redirect("home")

@login_required(login_url='/login/')
def profile(request):
    user = get_object_or_404(Profile, user=request.user)
    try:
        posts = Post.objects.filter(profile=user).order_by("-date")
    except ObjectDoesNotExist:
        posts = []

    ctx = {
        "profile": user,
        "user_posts": user,
        "posts": posts,
        "following_count": Follow.objects.filter(profile=user).count(),
        "followers_count": Follow.objects.filter(following=user).count(),
        "form_search": SearchForm()
    }
    return render(request, "profile.html", ctx)

def profileUtilizador(request,username):
    user_posts = get_object_or_404(Profile, user__username = username)

    if request.user.is_authenticated:
        user = get_object_or_404(Profile, user=request.user)
    else:
        user = None

    try:
        posts = Post.objects.filter(profile=user_posts).order_by("-date")
    except ObjectDoesNotExist:
        posts = []

    ctx = {
        "user_posts": user_posts,
        "posts": posts,
        "profile": user,
        "is_follower": Follow.objects.filter(following=user_posts, profile=user).exists(),
        "following_count": Follow.objects.filter(profile=user_posts).count(),
        "followers_count": Follow.objects.filter(following=user_posts).count(),
        "form_search": SearchForm()
    }

    return render(request, "profile.html", ctx)

@login_required(login_url='/login/')
def editProfile(request, username):
    if request.user.username != username:
        return redirect("profile")
    sucesso = False
    utilizador = get_object_or_404(Profile, user=request.user)
    ctx={
        "profile": utilizador,
        "form_search": SearchForm()
        }

    if request.method == "POST" and 'image' in request.FILES:
        formImage= ImageForm(request.POST, request.FILES)
        if formImage.is_valid():
            file = formImage.cleaned_data["image"]
            if file:
                utilizador.profile_pic = file
                utilizador.update_image(file)
                utilizador.save()
                sucesso = True

    if request.method == "POST" and 'old_password' in request.POST and 'new_password' in request.POST and 'password_confirm' in request.POST:
        formPassword= PasswordForm(request.POST)
        if formPassword.is_valid():
            old_password = formPassword.cleaned_data["old_password"]
            new_password = formPassword.cleaned_data["new_password"]
            password_confirm = formPassword.cleaned_data["password_confirm"]
            if new_password != password_confirm:
                sucesso = False
            else:

                if request.user.check_password(old_password):
                    request.user.set_password(new_password)
                    request.user.save()

                    utilizador.update_password(new_password)
                    utilizador.save()
                    sucesso = True
                else:
                    sucesso = False

    if request.method == "POST" and 'bio' in request.POST:
        formBio= BioForm(request.POST)
        if formBio.is_valid():
            bio = formBio.cleaned_data["bio"]
            if bio:
                utilizador.bio = bio
                utilizador.save()
                sucesso = True

    if not sucesso:
        ctx["formImage"] = ImageForm()
        ctx["formBio"] = BioForm()
        ctx["formPassword"] = PasswordForm()

        return render(request, "profileedit.html", ctx)

    return redirect("/profile")


# * Post*
@login_required(login_url='/login/')
def postadd(request):
    user = get_object_or_404(User, username=request.user.username)
    profile = get_object_or_404(Profile, user = user)
    if request.method == "POST" and request.FILES:
        caption = request.POST["caption"]
        photo = request.FILES["photo"]

        if caption and photo:
            Post.objects.create(profile=profile, image=photo, caption=caption)
            return redirect("home")
    else:
        return redirect("home")

def postdetail(request, _id):
    post = get_object_or_404(Post, id=_id)
    ctx = {
        "post": post,
        "comments": Comment.objects.filter(post=_id),
        "exist_like" : False,
        "form_search": SearchForm()
    }
    post=get_object_or_404(Post, id=_id)
    if request.user.is_authenticated and request.user.username!="admin":
        profile = get_object_or_404(Profile, user = request.user)
        ctx["profile"]= profile
        if request.method == "POST":
            form_comment = CommentForm(request.POST)
            if form_comment.is_valid():
                comment = form_comment.cleaned_data["comment"]
                Comment.objects.create(profile=profile, post=post, comment=comment)
                post.add_comment()
                return redirect("postdetail", _id)
        else:
            ctx["form_comment"] = CommentForm()
            ctx["exist_like"] = True

            return render(request, "postdetail.html", ctx)
    else:
        return render(request, "postdetail.html", ctx)

@login_required(login_url='/login/')
def postdelete(request, _id):
    post = get_object_or_404(Post, id=_id)
    if request.user.username == post.profile.user.username:
        post.delete()
        return redirect("home")
    else:
        return redirect("postdetail", _id)

@login_required(login_url='/login/')
def commentdelete(request,_id, _id_comment):
    post = get_object_or_404(Post, id=_id)
    comment = get_object_or_404(Comment, id=_id_comment)
    if request.user.username == comment.profile.user.username or request.profile.user.username == post.profile.user.username:
        post.remove_comment()
        comment.delete()
        return redirect("postdetail", comment.post.id)
    else:
        return redirect("postdetail", comment.post.id)

@login_required(login_url='/login/')
def postedit(request,_id):
    post = get_object_or_404(Post, id=_id)
    if request.user.username == post.profile.user.username:
        ctx = {
            "post": post,
            "form_postedit": EditPostForm(),
            "profile": Profile.objects.get(user=request.user),
            "form_search": SearchForm()
        }
        if request.method == "POST":
            form_postedit = EditPostForm(request.POST, request.FILES)
            ctx["form_postedit"]=form_postedit
            if form_postedit.is_valid():
                caption = form_postedit.cleaned_data["caption"]
                image = form_postedit.cleaned_data["image"]

                if image :
                    post.image = image
                    sucesso = True
                if caption:
                    post.caption = caption
                    sucesso = True
                if sucesso:
                    post.save()
                    return redirect("postdetail", _id)

        else:
            return render(request, "postedit.html", ctx)
    else:
        return redirect("postdetail", _id)


def like(request):
    if request.POST.get('action') == 'post':
        type = ''
        result = ''
        post_id = request.POST.get('post_id')
        user_id = request.POST.get('user_id')
        user = get_object_or_404(Profile, id=user_id)
        post = get_object_or_404(Post, id=post_id)
        if post.likes.filter(id=user_id).exists():
            post.remove_like(user)
            type = 'unlike'
            result = post.like_count
        else:
            type = 'like'
            post.add_like(user)
            result = post.like_count
        return JsonResponse({'result': result, 'type': type})

def follow(request):
    print("ola")
    if request.POST.get('action') == 'post':
        following = ''
        followers = ''
        user_id = request.POST.get('user_id')
        user_post_id = request.POST.get('user_posts_id')
        user = get_object_or_404(Profile, id=user_id)
        user_post = get_object_or_404(Profile, id=user_post_id)
        
        if Follow.objects.filter(profile=user, following=user_post).exists():
            print("unfollow")
            Follow.objects.filter(profile=user, following=user_post).delete()
            type = 'unfollow'
            following = Follow.objects.filter(profile=user_post).count()
            followers = Follow.objects.filter(following=user_post).count()
        else:
            Follow.objects.create(profile=user, following=user_post)
            type = 'follow'
            following = Follow.objects.filter(profile=user_post).count()
            followers = Follow.objects.filter(following=user_post).count()
        
        return JsonResponse({'type': type, 'following': following, 'followers': followers})

def error404(request, exception):
    user=None
    if request.user.is_authenticated and request.user.username!="admin":
        user = get_object_or_404(Profile, user=request.user)
    ctx = {
        "form_search": SearchForm(),
        "exception": exception,
        "profile": user
    }
    return render(request, '404.html',ctx)

def error500(request):
    user=None
    if request.user.is_authenticated and request.user.username!="admin":
        user = get_object_or_404(Profile, user=request.user)
    ctx = {
        "form_search": SearchForm(),
        "profile": user
    }
    return render(request, '404.html',ctx)

def searchuser(request):
    if request.method == "POST":
        form_search = SearchForm(request.POST)
        if form_search.is_valid():
            search = form_search.cleaned_data["search"]
            user = get_object_or_404(Profile, user=request.user)
            users = Profile.objects.filter(user__username__icontains=search).exclude(user__username__icontains=request.user.username)

            result = []
            for result_user in users:
                following = Follow.objects.filter(profile=result_user).count()
                followers = Follow.objects.filter(following=result_user).count()
                result.append((result_user,following,followers))
            ctx = {
                "form_search": SearchForm(),
                "profile": user,
                "result": result,
            }
            return render(request, "searchresult.html", ctx)
    else:
        return redirect("searchresult")

def searchresult(request):
    ctx={"form_search": SearchForm()}
    try:
        user = Profile.objects.get(user__username=request.user.username)
        ctx["profile"]=user
    except ObjectDoesNotExist:
        user = None

    return render(request, "searchresult.html", ctx)

@login_required(login_url="/login/")
def listFollower(request,username):
    user = get_object_or_404(Profile, user__username=username)
    followers = Follow.objects.filter(following=user)

    result = []
    for result_user in followers:
        print(result_user)
        following = Follow.objects.filter(profile=result_user.profile).count()
        followers = Follow.objects.filter(following=result_user.profile).count()
        result.append((result_user.profile,following,followers))
    ctx = {
        "form_search": SearchForm(),
        "profile": user,
        "result": result,
    }
    return render(request, "searchresult.html", ctx)

@login_required(login_url="/login/")
def listFollowing(request,username):
    user = get_object_or_404(Profile, user__username=username)
    followings = Follow.objects.filter(profile=user)
    result = []
    for result_user in followings:
        following = Follow.objects.filter(profile=result_user.following).count()
        followers = Follow.objects.filter(following=result_user.following).count()
        result.append((result_user.following,following,followers))
    ctx = {
        "form_search": SearchForm(),
        "profile": user,
        "result": result,
    }

    return render(request, "searchresult.html", ctx)

def search_filter(request):
    if request.method == "GET":
        query = request.GET.get('q')
        min_likes = request.GET.get('min_likes')
        max_likes = request.GET.get('max_likes')
        min_date = request.GET.get('min_date')
        max_date = request.GET.get('max_date')
        min_comments = request.GET.get('min_comments')
        max_comments = request.GET.get('max_comments')
        posts = Post.objects.all()
        hashtags = Hashtag.objects.all()
        if query:
            posts = posts.filter(caption__contains=query)
        if min_likes:
            posts = posts.filter(like_count__gte=min_likes)
        if max_likes:
            posts = posts.filter(like_count__lte=max_likes)
        if min_date:
            posts = posts.filter(date__gte=min_date)
        if max_date:
            posts = posts.filter(date__lte=max_date)
        if min_comments:
            posts = posts.filter(comment_count__gte=min_comments)
        if max_comments:
            posts = posts.filter(comment_count__lte=max_comments)

        context = {'posts': posts, "hashtags":hashtags, "form_search": SearchForm()}

        return render(request, 'filter.html', context)
