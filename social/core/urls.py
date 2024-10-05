from django.urls import path
from . import views
from .views import delete_notification, comment_post

urlpatterns = [
    path('defaultsite', views.index, name='index'),
    path('', views.index, name='index'),
    path('comment-post/<uuid:post_id>/', comment_post, name='comment_post'),
    path('delete_post/<post_id>/', views.delete_post, name='delete_post'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('settings', views.settings, name='settings'),
    path('upload', views.upload, name='upload'),
    path('delete_notification/<int:notification_id>/', delete_notification, name='delete_notification'),
    path('follow', views.follow, name='follow'),
    path('search', views.search, name='search'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('like-post/', views.like_post, name='like-post'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
]