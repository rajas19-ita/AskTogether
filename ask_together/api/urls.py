from django.urls import path
from . import views

urlpatterns = [
    path("answers/create/",views.create_answer, name="answer_create"),
    path("users/<int:pk>/posts/", views.get_posts, name="get_posts"),
    path("questions/<int:pk>/vote/", views.vote_question, name="vote_question"),
    path("answers/<int:pk>/vote/", views.vote_answer, name="vote_answer"),
    path("comments/create/", views.create_comment, name="comment_create"),
    path("questions/<int:pk>/accept/", views.accept_answer, name="answer_accept"),
    path("comments/", views.get_comments, name="get_comments"),
    path("check-username/", views.check_username, name="check_username"),
    path('notifications/', views.get_notifications, name="get_notifications"),
    path('notifications/count/',views.get_notifications_count, name="get_notifications_count")
]
