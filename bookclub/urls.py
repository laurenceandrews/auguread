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
import schedule
from clubs import views
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from schedule import views as schedule_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),

    path('sign_up/', views.sign_up, name='sign_up'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path("__reload__/", include("django_browser_reload.urls")),
    path('password/', views.PasswordView.as_view(), name='password'),

    path('user/<int:user_id>', views.ShowUserView.as_view(), name='show_user'),
    path('editprofile/<int:user_id>', views.EditUserView.as_view(), name='edit_user'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    # path('rec/', views.RecommendationsView.as_view(), name='rec_page'),


    path('feed/', views.FeedView.as_view(), name='feed'),
    # path('new_post/', views.new_post, name='new_post'),
    path('follow_toggle/<int:user_id>', views.follow_toggle, name='follow_toggle'),


    path('rec/', views.RecommendationsView, name='rec'),

    # path('users/', views.UserListView.as_view(), name='user_list'),
    path('<int:club_id>/user/<int:user_id>', views.ShowUserView.as_view(), name='show_user'),
    path('<int:club_id>/users', views.UserListView.as_view(), name='user_list'),

    path('clubs/', views.club_list, name='club_list'),
    path('new_club/', views.new_club, name='new_club'),
    path('new_post/', views.NewPostView.as_view(), name='new_post'),

    path('enter/<int:club_id>', views.enter, name='enter'),
    path('apply/<int:club_id>', views.apply, name='apply'),
    path('<int:club_id>/approve/<int:user_id>', views.approve, name='approve'),

    path('<int:club_id>/applicants', views.ApplicantListView.as_view(), name='applicant_list'),
    path('<int:club_id>/members', views.MemberListView.as_view(), name='member_list'),
    path('<int:club_id>/officers', views.OwnerListView.as_view(), name='owner_list'),

    path('user_detail/', views.user_detail, name='user_detail'),
    path('<int:club_id>/approve/<int:user_id>', views.approve, name='approve'),
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('follow_toggle/<int:user_id>', views.follow_toggle, name='follow_toggle'),

    # sample scheduler
    # url(r'^fullcalendar', TemplateView.as_view(template_name="fullcalendar.html"), name='fullcalendar'),


    url(r'^event/create/(?P<calendar_id>[-\w]+)/$',
        views.create_event,
        name='create_event'),
    path('full_calendar/<str:calendar_slug>', views.full_calendar, name='full_calendar'),
    path('calendar_picker/', views.calendar_picker, name='calendar_picker'),
    path('events_list/<int:calendar_id>', views.events_list, name='events_list'),
    path('event/<int:event_id>/link', views.create_event_link, name='create_event_link'),
    path('event/<int:event_id>/address', views.create_event_address, name='create_event_address'),
    # keep this at the end of the list to allow overwriting of unwanted urls
    url(r'^schedule/', include('schedule.urls')),
    path('club_recommender/', views.club_recommender, name='club_recommender'),

    path('book_preferences/', views.book_preferences, name='book_preferences')
    # path('book_preferences/', views.book_preferences, include('star_ratings.urls'), name='book_preferences')

]
