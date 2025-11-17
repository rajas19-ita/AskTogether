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
    path("users/edit/", views.UserUpdateView.as_view(),name='user_profile_edit'),
    path("users/account-setup/", views.AccountSetupView.as_view(), name="account_setup"),
    path("auth/password-reset/", views.PasswordReset.as_view(),name="password_reset"),
    path("auth/password-reset/done/", views.PasswordResetDone.as_view(),name="password_reset_done"),
    path("auth/reset/<uidb64>/<token>/", views.PasswordResetConfirm.as_view(),name="password_reset_confirm"),
    path("auth/reset/done/", views.PasswordResetComplete.as_view(), name="password_reset_complete"),
    path("auth/google/login/", views.GoogleLoginView.as_view(), name="google_login"),
    path("auth/google/callback/", views.GoogleCallbackView.as_view(), name="google_callback"),
    path('api/',include('ask_together.api.urls'))
]