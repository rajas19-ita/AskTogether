from django.urls import path,include
from . import views

app_name = 'ask_together'
urlpatterns = [
    path("",views.HomePageView.as_view(), name="home"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("questions/create/",views.QuestionCreateView.as_view(), name='question_create'),
    path("questions/<int:pk>/", views.QuestionDetailView.as_view(), name='question_detail'),
    path("users/<int:pk>/", views.UserDetailView.as_view(), name='user_profile'),
    path("users/edit", views.UserUpdateView.as_view(),name='user_profile_edit'),
    path('api/',include('ask_together.api.urls'))
]