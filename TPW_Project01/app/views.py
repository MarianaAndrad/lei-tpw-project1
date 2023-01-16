from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from app.forms import FormSingup, FormLogin, CommentForm, ImageForm, PasswordForm, BioForm, EditPostForm, SearchForm, CategoriaForm
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from app.models import Profile, Post, Comment, Follow,Hashtag, Categoria
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.db.models import Sum, Q, Count


def home(request):
    if request.user.is_authenticated:
        ctx = {
            "friend":True,
            "profile": get_object_or_404(Profile, user=request.user),
            "posts": Post.objects.all().order_by("-date").filter(categoria=get_object_or_404(Profile, user=request.user).categoria),
            "hashtags": Hashtag.objects.all(),
            "categorias": Categoria.objects.all(),
            "exist": True
        }

        return render(request, "home.html", ctx)
    else:
        ctx={
            "friend": False,
            "posts": Post.objects.all().order_by("-date"),
            "categorias": Categoria.objects.all(),
            "exist": False
        }
        return render(request, "home.html", ctx)

def home_categoria(request, _id):
    if request.user.is_authenticated:
        ctx = {
            "friend":True,
            "profile": get_object_or_404(Profile, user=request.user),
            "posts": Post.objects.all().order_by("-date").filter(categoria=_id),
            "hashtags": Hashtag.objects.all(),
            "categorias": Categoria.objects.all(),
            "exist": True
        }

        return render(request, "home.html", ctx)
    else:
        ctx={
            "friend": False,
            "posts": Post.objects.all().order_by("-date").filter(categoria=_id),
            "categorias": Categoria.objects.all(),
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
            categoria = formSignup.cleaned_data["categoria"]

            if password == confirmation:
                if User.objects.filter(username=username).exists():
                    return render(request, "signup.html", {"messages": "Username already exists." , "formSignup": formSignup})
                elif User.objects.filter(email=email).exists():
                    return render(request, "signup.html", {"messages": "Email already exists.", "formSignup": formSignup})
                elif categoria == None:
                    return render(request, "signup.html", {"messages": "Seleciona Categoria", "formSignup": formSignup})
                elif request.FILES:
                    photo = request.FILES["photo"]
                    user = User.objects.create_user(username=username, password=password, email=email)
                    profile = Profile.objects.create(user=user, profile_pic=photo,  categoria=categoria)
                    profile.save()
                    auth_login(request, User.objects.get(username=username))
                    return redirect("home")
                else:
                    user = User.objects.create_user(username=username, password=password, email=email)
                    user.save()
                    profile = Profile.objects.create(user=user, categoria=categoria)
                    profile.save()
                    auth_login(request, user)
                    return redirect("home")

            else:
                return render(request, "signup.html", {"messages": "Passwords do not match.", "formSignup": formSignup})
        else:
            return render(request, "signup.html", {"messages": "Invalid credentials.", "formSignup": formSignup})

    else:
        return render(request, "signup.html", {"formSignup": FormSingup()})

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
                    return render(request, "login.html", {"messages": "Invalid credentials.", "formLogin": formLogin,})
            else:
                return render(request, "login.html", {"messages": "Invalid credentials.", "formLogin": formLogin, })
        else:
            return render(request, "login.html", {"formLogin": FormLogin(),})

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
        "hashtags": Hashtag.objects.all(),
        "following_count": Follow.objects.filter(profile=user).count(),
        "followers_count": Follow.objects.filter(following=user).count(),
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
        "hashtags": Hashtag.objects.all(),
        "is_follower": Follow.objects.filter(following=user_posts, profile=user).exists(),
        "following_count": Follow.objects.filter(profile=user_posts).count(),
        "followers_count": Follow.objects.filter(following=user_posts).count(),
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
        "hashtags": Hashtag.objects.all(),
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

    if request.method == "POST" and 'categoria' in request.POST:
        formCategoria= CategoriaForm(request.POST)
        if formCategoria.is_valid():
            categoria = formCategoria.cleaned_data["categoria"]
            if categoria:
                utilizador.categoria = categoria
                utilizador.save()
                sucesso = True

    if not sucesso:
        ctx["formImage"] = ImageForm()
        ctx["formBio"] = BioForm()
        ctx["formPassword"] = PasswordForm()
        ctx["formCategoria"] = CategoriaForm()

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
            post = Post.objects.create(profile=profile, image=photo, caption=caption, categoria=profile.categoria)
            for hashtag in Hashtag.objects.all():
                if hashtag.hashtag in request.POST.keys():
                    post.add_hashtag(hashtag)

            return redirect("home")
    else:
        return redirect("home")

def postdetail(request, _id):
    post = get_object_or_404(Post, id=_id)
    ctx = {
        "post": post,
        "comments": Comment.objects.filter(post=_id),
        "hashtags": Hashtag.objects.all(),
        "exist_like" : False,
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
            "hashtags": Hashtag.objects.all(),
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
        "exception": exception,
        "profile": user
    }
    return render(request, '404.html',ctx)

def error500(request):
    user=None
    if request.user.is_authenticated and request.user.username!="admin":
        user = get_object_or_404(Profile, user=request.user)
    ctx = {
        "profile": user
    }
    return render(request, '404.html',ctx)

def searchuser(request):
    ctx={
    "form_search": SearchForm(),
    "hashtags": Hashtag.objects.all(),
    }
    if request.method == "POST":
        form_search = SearchForm(request.POST)
        if form_search.is_valid():
            search = form_search.cleaned_data["search"]
            try:
                user = get_object_or_404(Profile, user = request.user)
                ctx["profile"] = user
            except ObjectDoesNotExist:
                user = None

            if user is None:
                users = Profile.objects.filter(user__username__icontains=search)
            else:
                users = Profile.objects.filter(user__username__icontains=search).exclude(user__username__icontains=request.user.username)

            result = []
            for result_user in users:
                following = Follow.objects.filter(profile=result_user).count()
                followers = Follow.objects.filter(following=result_user).count()
                result.append((result_user,following,followers))

            ctx["result"]=result
            return render(request, "searchresult.html", ctx)
    else:
        try:
            user = get_object_or_404(Profile, user = request.user)
            ctx["profile"] = user
        except ObjectDoesNotExist:
            user = None

        if user is None:
            users = Profile.objects.all()
        else:
            users = Profile.objects.exclude(user__username__icontains=request.user.username)

        result = []
        for result_user in users:
            following = Follow.objects.filter(profile=result_user).count()
            followers = Follow.objects.filter(following=result_user).count()
            result.append((result_user,following,followers))
        
        ctx["result"]=result
            
        return render(request, "searchresult.html", ctx)

def searchresult(request):
    ctx={
        "form_search": SearchForm(),
        "hashtags": Hashtag.objects.all(),
        }
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
        "hashtags": Hashtag.objects.all(),
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
        "hashtags": Hashtag.objects.all(),
    }

    return render(request, "searchresult.html", ctx)

def search_filter(request):
        query = request.GET.get('search')
        likes = request.GET.get('likes')
        min_date = request.GET.get('min_date')
        max_date = request.GET.get('max_date')
        comments = request.GET.get('comments')
        categoria = request.GET.get('categoria')
        if categoria == "0":
            categoria = None
        posts = Post.objects.all()
        query_objects = Q()
        if query:
            query_objects |= Q(caption__contains=query)
        if categoria:
            query_objects |= Q(categoria=categoria)
        if likes:
            query_objects &= Q(like_count__gte=likes)
        if min_date:
            query_objects &= Q(date__gte=min_date)
        if max_date:
            query_objects &= Q(date__lte=max_date)
        if comments:
            query_objects &= Q(comment_count__gte=comments)

        posts = posts.filter(query_objects)

        list_hashtags=[]
        for hashtag in Hashtag.objects.all():
            if hashtag.hashtag in request.GET.keys():
                posts = posts.filter(hashtags=hashtag)
                list_hashtags.append(hashtag.hashtag)


        context = {
            "hashtags": Hashtag.objects.all(), 
            "number_comments":Comment.objects.all().count(),
            "number_likes":count_likes_total(),
            "list_hashtags": list_hashtags,
            "categorias": Categoria.objects.all(),
            }

        if len(posts)!= 0:
            context["posts"] = posts
        
        try:
            user = Profile.objects.get(user__username=request.user.username)
            context["profile"]=user
        except ObjectDoesNotExist:
            user = None


        return render(request, 'filter.html', context)


def hashtag_list(request, hashtag):
    posts = Post.objects.filter(hashtags=get_object_or_404(Hashtag, hashtag=hashtag))
    ctx = {
        'posts': posts,
        "hashtags": Hashtag.objects.all(),
        }

    try:
        user = Profile.objects.get(user__username=request.user.username)
        ctx["profile"]=user
    except ObjectDoesNotExist:
        user = None

    return render(request, 'home.html', ctx)

# **Graficos**

def statistic(request): 
    ctx=ctx_static()
    try:
        user = Profile.objects.get(user__username=request.user.username)
        ctx["profile"]=user

    except ObjectDoesNotExist:
        user = None
    try:
        user = Profile.objects.get(user__username=request.user.username)
        ctx["profile"]=user

    except ObjectDoesNotExist:
        user = None

    return render(request, "statistic.html", ctx)


def graphics(request, type):
    ctx = ctx_static()
    try:
        user = Profile.objects.get(user__username=request.user.username)
        ctx["profile"]=user
    except ObjectDoesNotExist:
        user = None

    if type in ["categoria", "hashtag"]:
        if type == "categoria":
            group_by = 'categoria__nome'
        elif type == "hashtag":
            group_by = 'hashtags__hashtag'

        ctx["titlelike"] = f"Total de likes por {type.capitalize()}"
        queryset = Post.objects.values(group_by).annotate(total=Sum('like_count'))
        ctx["labelslike"] = [entry[group_by] for entry in queryset]
        ctx["datalike"] = [entry['total'] for entry in queryset]

        ctx["titlecomment"] = f"Total de comments por {type.capitalize()}"
        queryset = Post.objects.values(group_by).annotate(total=Sum('comment_count'))
        ctx["labelscomment"] = [entry[group_by] for entry in queryset]
        ctx["datacomment"] = [entry['total'] for entry in queryset]

        ctx["titlepost"] = f"Total de posts por {type.capitalize()}"
        queryset = Post.objects.values(group_by).annotate(total=Count(group_by))
        ctx["labelspost"] = [entry[group_by] for entry in queryset]
        ctx["datapost"] = [entry['total'] for entry in queryset]

        return render(request, 'statistic.html', ctx)
    else: 
        return render(request, '404.html')

        
@login_required(login_url="/login/")
def graphics_user(request, type):
    ctx = ctx_static()
    try:
        user = Profile.objects.get(user__username=request.user.username)
        ctx["profile"]=user

    except ObjectDoesNotExist:
        user = None

    if type in ["categoria", "hashtag","date"]:
        if type == "categoria":
            group_by = 'categoria__nome'
        elif type == "hashtag":
            group_by = 'hashtags__hashtag'
        

        ctx["titlelike"] = f"Total de likes por {type.capitalize()}"
        queryset = Post.objects.filter(profile__user__username=request.user.username).values(group_by).annotate(total=Sum('like_count'))
        ctx["labelslike"] = [entry[group_by] for entry in queryset]
        ctx["datalike"] = [entry['total'] for entry in queryset]

        ctx["titlecomment"] = f"Total de comments por {type.capitalize()}"
        queryset = Post.objects.filter(profile__user__username=request.user.username).values(group_by).annotate(total=Sum('comment_count'))
        ctx["labelscomment"] = [entry[group_by] for entry in queryset]
        ctx["datacomment"] = [entry['total'] for entry in queryset]

        ctx["titlepost"] = f"Total de posts por {type.capitalize()}"
        queryset = Post.objects.filter(profile__user__username=request.user.username).values(group_by).annotate(total=Count(group_by))
        ctx["labelspost"] = [entry[group_by] for entry in queryset]
        ctx["datapost"] = [entry['total'] for entry in queryset]

        return render(request, 'statistic.html', ctx)
    else: 
        return render(request, '404.html')

# *Funções auxiliares*

def count_likes_total():
    posts =Post.objects.all()
    count = 0
    for post in posts:
        count += post.like_count
    return count

def ctx_static():
    ctx={
    "list_types":[
        ("Categorias", "categoria"),
        ("Hashtags", "hashtag")
        ],
    }
    return ctx

