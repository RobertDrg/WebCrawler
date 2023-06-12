from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login_user', views.login_user, name="login"),
    path('logout_user', views.logout_user, name="logout"),
    path('register_user', views.register_user, name="register_user"),
    path('edit_profile/', views.UserEditView.as_view(), name="edit_profile"),
    path('edit_profile/{}', views.PasswordsChangeView.as_view(template_name='authenticate/change_password.html')),
]
