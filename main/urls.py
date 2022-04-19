from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name="index"),
    path('test/', views.test, name="test"),
    path('post/<int:comment_id>/', views.comment_like, name='like'),
    path('category/<int:category_id>/', views.category, name='category'),
    path('category/<int:category_id>/new/', views.new_post, name='new post'),
    path('category/<int:category_id>/<int:post_id>/', views.post_view, name='post'),
    path('category/<int:category_id>/<int:post_id>/new', views.new_comment, name='comment'),
    path('chat/', views.chat, name="chat"),
    path('chat/new/', views.new_chat_msg, name="new chat message"),
    path('account/', views.account, name="account"),
    path('account/edit/', views.account_edit, name="edit account"),
    path('account/post/', views.account_post, name="edit account"),
    path('account/login/', views.Login.as_view(), name="login"),
    path('account/logout/', views.logout_view, name="logout"),
    path('account/profile/', views.profile, name="profile"),
    path('account/register/', views.register, name="register"),
    path('search/', views.search_post, name="search_post"),
]
