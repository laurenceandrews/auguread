"""bookclub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from clubs import views
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('', views.home, name='home'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path("__reload__/", include("django_browser_reload.urls")),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('user/<int:user_id>', views.ShowUserView.as_view(), name='show_user'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    # path('rec/', views.RecommendationsView.as_view(), name='rec_page'),
    path('rec/', views.RecommendationsView, name='rec'),
    path('clubs/', views.ClubListView.as_view(), name='club_list'),
    path('new_club/', views.NewClubView.as_view(), name='new_club'),
    path('new_post/', views.NewPostView.as_view(), name='new_post'),
    # sample scheduler
    url(r'^schedule/', include('schedule.urls')),
    url(r'^fullcalendar/', TemplateView.as_view(template_name="fullcalendar.html"), name='fullcalendar'),
]
