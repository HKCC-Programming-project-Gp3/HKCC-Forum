from django import template
from django.utils import timesince
from ..models import PostComment, User

register = template.Library()


@register.filter
def is_liked(post_comment: PostComment, user: User):
    if user.is_authenticated:
        return post_comment.postlike_set.filter(user=user.forumuser).count() != 0
    return False


@register.filter
def is_disliked(post_comment: PostComment, user: User):
    if user.is_authenticated:
        return post_comment.postdislike_set.filter(user=user.forumuser).count() != 0
    return False


@register.filter
def sub_like(comment: PostComment):
    if comment is None:
        return None
    return comment.like - comment.dislike


@register.filter
def pos_like(comment: PostComment):
    if comment is None:
        return None
    return comment.like >= comment.dislike


@register.filter
def timesince2(time):
    return timesince.timesince(time, depth=1).replace("hours", "h").replace("hour", "h").replace("minutes", "m").replace("minute", "m")


@register.filter
def br_replace(text):
    return text.replace("\n", "<br>")
