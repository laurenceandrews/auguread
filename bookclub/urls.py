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
from clubs.views.recommender_views import ClubRecommenderView
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from schedule.views import (DeleteEventView, EditEventView, EventView,
                            api_move_or_resize_by_code, api_occurrences,
                            api_select_create)

urlpatterns = [
    # Admin urls
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),

    path('rec/', views.RecommendationsView.as_view(), name='rec'),
    path('book_preferences/', views.BookPreferencesView.as_view(), name='book_preferences'),
    path('club_recommender/', ClubRecommenderView.as_view(), name='club_recommender'),
    url(r"^club/book/recommendations/(?P<club_id>\d+)/$", views.RecommendedClubBookListView.as_view(), name='club_book_recommendations'),
    url(r"^club/(?P<club_id>\d+)/book/(?P<book_id>\d+)/select/$", views.club_book_select_view, name='club_book_select'),

    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path("__reload__/", include("django_browser_reload.urls")),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('edit_profile/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('user/settings/', views.settings_view, name='settings'),
    path('user/delete/', views.delete_account, name='delete_account'),
    path('user/profile/', views.user_profile_view, name='user_profile'),
    path('user/detail/<int:user_id>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/', views.UserDetailList.as_view(), name='user_detail_list'),

    path('summary/', views.UserSummaryView.as_view(), name='user_summary'),
    path('summary/clubs/<str:role_num>', views.clubs_list, name='user_clubs'),
    path('summary/books/favourite', views.user_favourite_books, name='user_favourite_books'),
    path('summary/books/clubs', views.user_clubs_books, name='user_clubs_books'),
    path('summary/books/current', views.user_current_book, name='user_current_book'),

    # Forgot Password urls
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Feed urls
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('new_post/', views.NewPostView.as_view(), name='new_post'),
    path('follow_toggle/<int:user_id>', views.follow_toggle, name='follow_toggle'),


    path('club/<int:club_id>/feed/create', views.ClubFeedPostCreateView.as_view(), name='club_vieed_create'),



    # Club urls
    path('clubs/', views.ClubListView.as_view(), name='club_list'),
    path('new_club/', views.new_club, name='new_club'),
    url(r"^club/detail/(?P<club_id>\d+)/$", views.ClubDetailView.as_view(), name='club_detail'),
    path('club/update/<int:club_id>', views.ClubUpdateView.as_view(), name='club_update'),
    path('club/delete/<int:club_id>', views.DeleteClubView.as_view(), name='club_delete'),



    path('enter/<int:club_id>', views.enter, name='enter'),
    path('apply/<int:club_id>', views.apply, name='apply'),
    path('<int:club_id>/approve/<int:user_id>', views.approve, name='approve'),
    path('<int:club_id>/transfer/<int:user_id>', views.transfer, name='transfer'),

    re_path(r"^club/user/delete/(?P<club_users_id>\d+)/$", views.DeleteClubUserView.as_view(), name="delete_club_user"),

    path('<int:club_id>/applicants', views.applicants_list, name='applicant_list'),
    path('<int:club_id>/members', views.members_list, name='member_list'),


    path('book/rating/<int:book_id>/', views.CreateBookRatingView.as_view(), name='rate_book'),

    path('user/<int:user_id>/book/<int:book_id>/history/', views.CreateUserBookHistoryView.as_view(), name='create_user_book_history'),

    path('user/<int:user_id>/book/<int:book_id>/favourite/', views.CreateUserBooksView.as_view(), name='create_user_book_favourite'),
    path('user/<int:user_id>/book/<int:book_id>/favourite/delete/', views.delete_user_book_favourite, name='delete_user_book_favourite'),

    url(r"^book/detail/(?P<book_id>\d+)/$", views.BookDetailView.as_view(), name='book_detail'),

    # Meeting scheduler urls
    re_path(r"^schedule/api/occurrences", api_occurrences, name="api_occurrences"),
    path('calendar_picker/', views.CalendarPickerView.as_view(), name='calendar_picker'),
    url(r"^fullcalendar/(?P<calendar_slug>[-\w]+)/$", views.full_calendar, name='full_calendar'),

    path('events_list/<int:calendar_id>', views.events_list, name='events_list'),
    url(r"^event/detail/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$", views.EventDetailView.as_view(), name='event_detail'),
    url(r'^event/create/(?P<calendar_slug>[-\w]+)/$', views.CreateEventView.as_view(), name='create_event'),
    url(r"^event/edit/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$", views.EditEventView.as_view(), name='edit_event'),
    re_path(r"^event/delete/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$", views.DeleteEventView.as_view(), name="delete_event"),
    url(r"^event/address/create/newaddress/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$", views.CreateAddressView.as_view(), name='create_address'),
    url(r"^event/address/create/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$", views.CreateEventAddressView.as_view(), name='create_event_address'),
    url(r"^event/address/edit/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$", views.EditEventAddressView.as_view(), name='edit_event_address'),
    url(r"^event/link/create/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$", views.CreateEventLinkView.as_view(), name='create_event_link'),
    url(r"^event/link/edit/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$", views.EditEventLinkView.as_view(), name='edit_event_link'),



]
