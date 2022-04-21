import json
from django.contrib import messages
from django.contrib.auth import views as auth_view, logout, login, authenticate
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.db.models import F, Q, QuerySet
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.clickjacking import xframe_options_exempt
from .forms import NewUserForm
from .models import Category, ChatMessage, Post, PostComment, PostLike, PostDislike, Tag, User
from .templatetags.main_extras import is_liked, is_disliked

from django.db.models import Q


def default_value(request, data=None):
    if data is None:
        data = {}
    data.update({"user": request.user})
    data.update({"categorys": Category.objects.filter(parent=None)})
    return data


def index(request):
    posts = Post.objects.all()
    return render(request, 'index.html', default_value(request, {"posts": posts}))


def category(request, category_id):
    category = Category.objects.get(id=category_id)
    return render(request, 'category.html', default_value(request, {"category": category}))


def new_post(request, category_id):
    if not request.user.is_authenticated:
        return redirect("login")
    category = Category.objects.get(id=category_id)
    if request.method == "POST":
        post = Post.objects.create(user=request.user.forumuser, category=category, title=request.POST["subject"])
        PostComment.objects.create(user=request.user.forumuser, post=post, comment_position=1,
                                   content=request.POST["content"])
        if request.POST['json_tag'] != "":
            tags = json.loads(request.POST['json_tag'])
            for i in tags:
                tag = Tag.objects.filter(name=i)
                if not tag:
                    tag = Tag.objects.create(name=i)
                    tag.save()
                else:
                    tag = tag[0]
                post.tag_set.add(tag)
                post.save()
        return redirect(f"/category/{category_id}/{post.id}")
    return render(request, 'new_post.html', default_value(request, {"category": category}))


def new_comment(request, category_id, post_id):
    if not request.user.is_authenticated:
        return redirect("login")
    post = Post.objects.get(id=post_id)
    if request.method == "POST":
        comments = post.postcomment_set
        last_comment = comments.last()
        if last_comment is None:
            position = 1
        else:
            position = last_comment.comment_position + 1
        if request.POST["reply_to"] != "":
            reply = post.postcomment_set.get(comment_position=request.POST["reply_to"])
        else:
            reply = None
        comment = PostComment.objects.create(user=request.user.forumuser, post=post, comment_position=position,
                                             content=request.POST["content"], quote=reply)
    return JsonResponse({"result": "success"})
    #return redirect(f"/category/{category_id}/{post_id}")


def post_view(request, category_id, post_id):
    category = Category.objects.get(id=category_id)
    post = Post.objects.get(id=post_id)
    if request.method == "POST":
        if request.POST['subview'] == 'true':
            return render(request, 'only_post.html', default_value(request, {"category": category, "post": post}))
    return render(request, 'post.html', default_value(request, {"category": category, "post": post}))


def comment_like(request, comment_id):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.method == "POST":
        comment = PostComment.objects.get(id=comment_id)
        data = request.POST
        if is_liked(comment, request.user) or is_disliked(comment, request.user):
            return redirect(request.POST["next"])
        if data["like"] == 'true':
            PostLike.objects.create(user=request.user.forumuser, post_comment=comment)
            comment.like += 1
            comment.save()
        else:
            PostDislike.objects.create(user=request.user.forumuser, post_comment=comment)
            comment.dislike += 1
            comment.save()
        return JsonResponse({"result": "success"})


def test(request):
    return render(request, 'test1.html', default_value(request))


class Login(auth_view.LoginView):
    template_name = "login.html"
    next_page = ""
    redirect_authenticated_user = True


def logout_view(request):
    logout(request)
    return redirect("login")


def register(request):
    if request.user.is_authenticated:
        return redirect("profile")
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("/")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = NewUserForm()
    return render(request, "register.html", {"form": form})


def chat(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.method == "GET" or request.method == "POST" and request.POST['subview'] == 'true':
        user = request.user.forumuser
        chats_cache = ChatMessage.objects.filter(Q(sender=user) | Q(receiver=user)).order_by("create_date")
        chats = chats_cache.all()
        for i in chats_cache:
            if i.sender != user:
                if chats.filter(Q(sender=i.sender) | Q(receiver=i.sender)).count() > 1:
                    chats = chats.exclude(id=i.id)
            elif i.receiver != user:
                if chats.filter(Q(sender=i.receiver) | Q(receiver=i.receiver)).count() > 1:
                    chats = chats.exclude(id=i.id)
        chats = chats.order_by(F("create_date").desc())
        if "name" in request.GET.keys() and request.GET["name"] != user.user.username or "name" in request.POST.keys() and request.POST["name"] != user.user.username:
            if request.method == "GET":
                current = User.objects.get(username=request.GET["name"]).forumuser
            else:
                current = User.objects.get(username=request.POST["name"]).forumuser
        elif chats.count() > 0:
            msg = chats.first()
            if msg.sender != user:
                current = msg.sender
            else:
                current = msg.receiver
        else:
            current = False
        current_chats = chats_cache.filter(Q(sender=current) | Q(receiver=current))
        if current_chats.count() == 0:
            new_chat = True
        else:
            new_chat = False
        if current == user:
            current = None
        if request.method == "GET":
            return render(request, 'chat.html', default_value(request, {"chats": chats, "current": current, "current_chats": current_chats, "new_chat": new_chat}))
        else:
            return render(request, 'only_chat.html', default_value(request, {"chats": chats, "current": current, "current_chats": current_chats, "new_chat": new_chat}))



def new_chat_msg(request):
    if request.method == "POST":
        sender = User.objects.get(username=request.POST["sender"]).forumuser
        receiver = User.objects.get(username=request.POST["receiver"]).forumuser
        ChatMessage.objects.create(sender=sender,receiver=receiver, content=request.POST["content"])
    return redirect("chat")


def account(request):
    if request.user.is_authenticated:
        return redirect("profile")
    else:
        return redirect("login")


def account_post(request):
    if not request.user.is_authenticated:
        return redirect("login")
    else:
        posts = Post.objects.filter(user=request.user.forumuser).order_by("create_date")
        return render(request, 'profile_post.html', default_value(request, {"posts": posts}))


def profile(request):
    if not request.user.is_authenticated:
        return redirect("login")
    else:
        post = Post.objects.filter(user=request.user.forumuser).order_by("create_date").last()
        return render(request, 'profile.html', default_value(request, {"post": post}))


def account_edit(request):
    if request.method == "POST":
        if check_password(request.POST["password"], request.user.password) and request.POST["new_password"] == request.POST["new_password2"]:
            try:
                validate_password(request.POST["new_password"], request.user)
                request.user.set_password(request.POST["new_password"])
                request.user.save()
                return render(request, 'profile_edit.html', default_value(request, {"success": "true"}))
            except Exception as e:
                return render(request, 'profile_edit.html', default_value(request, {"errors": e}))
        else:
            return render(request, 'profile_edit.html', default_value(request, {"pass_not_correct": "the password is not correct"}))
    return render(request, 'profile_edit.html', default_value(request))


def search_post(request):
    if request.GET.get("search") != '' and request.GET.get("search")[0] == '#':
        query = request.GET.get("search")[1:]
        results = Post.objects.filter(
            Q(tag__name__icontains=query)
        )
    else:
        query = request.GET.get("search")
        results = Post.objects.filter(
            Q(title__icontains=query) | Q(tag__name__icontains=query)
        )
    return render(request, 'index.html', default_value(request, {"posts": results}))
