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
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from schedule.views import (DeleteEventView, EditEventView, EventView,
                            api_move_or_resize_by_code, api_occurrences,
                            api_select_create)

urlpatterns = [
    # Admin urls
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),

    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path("__reload__/", include("django_browser_reload.urls")),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('rec/', views.RecommendationsView, name='rec'),

    # User urls
    path('<int:club_id>/user/<int:user_id>', views.ShowUserView.as_view(), name='show_user'),
    path('<int:club_id>/users', views.UserListView.as_view(), name='user_list'),
    path('user_detail/', views.user_detail, name='user_detail'),

    # Feed urls
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('new_post/', views.NewPostView.as_view(), name='new_post'),
    path('follow_toggle/<int:user_id>', views.follow_toggle, name='follow_toggle'),

    # Club urls
    path('clubs/', views.ClubListView.as_view(), name='club_list'),
    path('new_club/', views.new_club, name='new_club'),

    path('enter/<int:club_id>', views.enter, name='enter'),
    path('apply/<int:club_id>', views.apply, name='apply'),
    path('<int:club_id>/approve/<int:user_id>', views.approve, name='approve'),
    path('<int:club_id>/transfer/<int:user_id>', views.transfer, name='transfer'),

    path('<int:club_id>/applicants', views.ApplicantListView.as_view(), name='applicant_list'),
    path('<int:club_id>/members', views.MemberListView.as_view(), name='member_list'),
    path('<int:club_id>/officers', views.OwnerListView.as_view(), name='owner_list'),

    path('user_detail/', views.user_detail, name='user_detail'),
    path('<int:club_id>/approve/<int:user_id>', views.approve, name='approve'),
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('follow_toggle/<int:user_id>', views.follow_toggle, name='follow_toggle'),

    # sample scheduler
    # url(r'^fullcalendar', TemplateView.as_view(template_name="fullcalendar.html"), name='fullcalendar'),

    # Meeting scheduler urls
    re_path(r"^schedule/api/occurrences", api_occurrences, name="api_occurrences"),
    path('calendar_picker/', views.calendar_picker, name='calendar_picker'),
    url(r"^fullcalendar/(?P<calendar_slug>[-\w]+)/$",
        views.full_calendar,
        name='full_calendar'),
    path('events_list/<int:calendar_id>', views.events_list, name='events_list'),
    url(r"^event/detail/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$",
        views.EventDetailView.as_view(),
        name='event_detail'),
    url(r'^event/create/(?P<calendar_id>[-\w]+)/$',
        views.CreateEventView.as_view(),
        name='create_event'),
    url(r"^event/address/create/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$",
        views.CreateEventAddressView.as_view(),
        name='create_event_address'),
    url(r"^event/address/create/newaddress/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$",
        views.CreateAddressView.as_view(),
        name='create_address'),
    url(r"^event/link/create/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$",
        views.CreateEventLinkView.as_view(),
        name='create_event_link'),
    url(r"^event/edit/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$",
        views.EditEventView.as_view(),
        name='edit_event'),
    url(r"^event/link/edit/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$",
        views.EditEventLinkView.as_view(),
        name='edit_event_link'),
    url(r"^event/address/edit/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$",
        views.EditEventAddressView.as_view(),
        name='edit_event_address'),
    re_path(r"^event/(?P<event_id>\d+)/$", EventView.as_view(), name="event"),
    re_path(
        r"^event/delete/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$",
        views.DeleteEventView.as_view(),
        name="delete_event",
    ),

    # Book recommender urls
    path('club_recommender/', views.club_recommender, name='club_recommender'),

    #path('book_preferences/', views.book_preferences, name='book_preferences'),
    path('book_preferences/', views.BookPreferencesView.as_view(), name='book_preferences'),


    url(r"^club/book/edit/(?P<club_id>\d+)/$",
        views.ClubBookSelectionView.as_view(),
        name='club_book_select'),
]
