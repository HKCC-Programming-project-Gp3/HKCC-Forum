from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.utils.timezone import now, timedelta


class ForumUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


@receiver(models.signals.post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        ForumUser.objects.create(user=instance)


@receiver(models.signals.post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.forumuser.save()


class Category(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):
    user = models.ForeignKey(ForumUser, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    title = models.TextField()
    create_date = models.DateTimeField(default=now, editable=False)

    def __str__(self):
        return self.title


class PostComment(models.Model):
    user = models.ForeignKey(ForumUser, on_delete=models.PROTECT)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    quote = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    comment_position = models.IntegerField()
    like = models.IntegerField(default=0)
    dislike = models.IntegerField(default=0)
    content = models.TextField()
    create_date = models.DateTimeField(default=now, editable=False)


class PostLike(models.Model):
    user = models.ForeignKey(ForumUser, on_delete=models.PROTECT)
    post_comment = models.ForeignKey(PostComment, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=now, editable=False)


class PostDislike(models.Model):
    user = models.ForeignKey(ForumUser, on_delete=models.PROTECT)
    post_comment = models.ForeignKey(PostComment, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=now, editable=False)


class Tag(models.Model):
    post = models.ManyToManyField(Post)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class ChatMessage(models.Model):
    sender = models.ForeignKey(ForumUser, related_name="send_messages", on_delete=models.PROTECT)
    receiver = models.ForeignKey(ForumUser, related_name="receive_messages", on_delete=models.PROTECT)
    content = models.TextField()
    create_date = models.DateTimeField(default=now, editable=False)
