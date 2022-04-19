from django.contrib import admin

from .models import ForumUser, Post, PostComment, Tag, Category, ChatMessage


admin.site.register(ForumUser)
admin.site.register(Post)
admin.site.register(PostComment)
admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(ChatMessage)
