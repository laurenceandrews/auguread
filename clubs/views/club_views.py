"""Views related to the clubs."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from clubs.models import Club
from clubs.forms import NewClubForm
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from clubs.helpers import member, owner
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

@login_required()
def new_club(request):
    if request.method == "POST":
        current_user = request.user
        form = NewClubForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            city = form.cleaned_data.get("city")
            country = form.cleaned_data.get("country")
            description = form.cleaned_data.get("description")
            avg_reading_speed = form.cleaned_data.get("avg_reading_speed")
            calendar_name = form.cleaned_data.get("calendar_name")

            location = city + ", " + country

            calendar_slug = slugify(calendar_name)
            cal = Calendar(name=calendar_name, slug=calendar_slug)
            cal.save()

            meeting_type = form.cleaned_data.get("meeting_type")

            club = Club.objects.create(
                name=name,
                location=location,
                description=description,
                avg_reading_speed=avg_reading_speed,
                owner=current_user,
                calendar=cal,
                meeting_type=meeting_type
            )
            return redirect("club_list")
        else:
            return render(request, "new_club.html", {"form": form})
    else:
        return render(request, "new_club.html", {"form": NewClubForm})


@login_required
def club_list(request):
    clubs = Club.objects.all()
    paginator = Paginator(clubs, settings.NUMBER_PER_PAGE)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'club_list.html',
        {
            "page_obj": page_obj,
            "clubs": clubs,
        }
    )


@login_required
@member
def enter(request, club_id):
    user = request.user
    return redirect('show_user', user_id=user.id, club_id=club_id)


@login_required
def apply(request, club_id):
    user = request.user
    club = Club.objects.get(id=club_id)
    club.applied_by(user)
    return redirect('club_list')


@login_required
@owner
def approve(request, user_id, club_id):
    club = Club.objects.get(id=club_id)
    try:
        user = User.objects.get(id=user_id)
        club.accept(user)
    except ObjectDoesNotExist:
        return redirect('applicant_list', club_id=club_id)
    else:
        return redirect('show_user', user_id=user.id, club_id=club_id)

@login_required
@owner
def transfer(request, user_id, club_id):
    club = Club.objects.get(id=club_id)
    try:
        target = User.objects.get(id=user_id)
        club.transfer(target)
    except ObjectDoesNotExist:
        return redirect('owner_list', club_id=club_id)
    else:
        return redirect('show_user', user_id=user_id, club_id=club_id)

    form = BookRatingForm()
    return render(request, 'book_preferences.html', {'current_user': request.user, 'books_queryset': books_queryset, 'books_paginated': books_paginated, 'form': form})
