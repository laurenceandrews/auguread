from clubs.forms import (AddressForm, CalendarPickerForm, CreateEventForm,
                         MeetingAddressForm, MeetingLinkForm)
from clubs.models import Address, Club, MeetingAddress, MeetingLink
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from schedule.models import Calendar, Event, Rule

from .helpers import login_prohibited
from .mixins import (ApplicantProhibitedMixin, LoginProhibitedMixin,
                     MemberProhibitedMixin)


@login_required
def calendar_picker(request):
    """ View to select a calendar to display its full calendar. """
    if request.method == 'POST':
        form = CalendarPickerForm(request.POST)
        if form.is_valid():
            calendar = form.cleaned_data.get('calendar')
            return render(request, 'fullcalendar.html', {'calendar': calendar})
    else:
        form = CalendarPickerForm()
    return render(request, 'calendar_picker.html', {'form': form})


@login_required
def full_calendar(request, calendar_slug):
    """ View to display a calendar's full calendar. """

    calendar = Calendar.objects.get(slug=calendar_slug)
    return render(request, 'fullcalendar.html', {'calendar': calendar})


@login_required
def events_list(request, calendar_id):
    """ View to display a calendar's event list. """
    calendar = Calendar.objects.get(id=calendar_id)
    events = calendar.event_set.all()
    return render(request, "events_list.html",
                  {
                      'calendar': calendar,
                      'events': events,
                  })


class CreateEventView(LoginRequiredMixin, CreateView):
    """ View to handle creating events. """

    model = Event
    template_name = 'event_create.html'
    form_class = CreateEventForm

    def form_valid(self, form):
        """Process a valid form."""
        calendar = Calendar.objects.get(id=self.kwargs['calendar_id'])

        title = form.cleaned_data.get('title')
        start = form.cleaned_data.get('start')
        end = form.cleaned_data.get('end')
        end_recurring_period = form.cleaned_data.get('end_recurring_period')
        rule = form.cleaned_data.get('rule')

        event = Event.objects.create(
            title=title,
            start=start,
            end=end,
            end_recurring_period=end_recurring_period,
            rule=rule,
            calendar=calendar
        )

        club = Club.objects.get(calendar=event.calendar)

        if club.meeting_type == 'ONL':
            return redirect('create_event_link', calendar_slug=calendar.slug, event_id=event.id)

        if club.meeting_type == 'INP':
            return redirect('create_event_address', calendar_slug=calendar.slug, event_id=event.id)

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        calendar = Calendar.objects.get(id=self.kwargs['calendar_id'])
        return reverse('full_calendar', kwargs={'calendar_slug': calendar.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar = Calendar.objects.get(id=self.kwargs['calendar_id'])
        context['calendar'] = calendar
        context['calendar_id'] = calendar.id
        context['calendar_name'] = calendar.name
        context['user'] = self.request.user

        return context


class CreateEventLinkView(LoginRequiredMixin, CreateView):
    """ View to handle createing event links for online clubs. """

    model = MeetingLink
    template_name = 'event_link_form.html'
    form_class = MeetingLinkForm

    def form_valid(self, form):
        """Process a valid form."""
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        event = Event.objects.get(id=self.kwargs['event_id'])

        meeting_link = form.cleaned_data.get('meeting_link')

        meeting_link_object = MeetingLink.objects.create(
            event=event,
            meeting_link=meeting_link
        )
        return render(self.request, 'fullcalendar.html', {'calendar': event.calendar})

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        return reverse('full_calendar', kwargs={'calendar_slug': calendar.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = Event.objects.get(id=self.kwargs['event_id'])
        context['event'] = event

        return context


class CreateEventAddressView(LoginRequiredMixin, CreateView):
    """ View to handle creating event addresses for in-person clubs. """

    model = MeetingAddress
    template_name = 'event_address_create.html'
    form_class = MeetingAddressForm

    def form_valid(self, form):
        """Process a valid form."""
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        event = Event.objects.get(id=self.kwargs['event_id'])

        address = form.cleaned_data.get('address')

        meeting_address_object = MeetingAddress.objects.create(
            event=event,
            address=address
        )
        return render(self.request, 'fullcalendar.html', {'calendar': event.calendar})

    def get_form_kwargs(self):
        kwargs = super(CreateEventAddressView, self).get_form_kwargs()
        kwargs['calendar_slug'] = self.kwargs['calendar_slug']
        return kwargs

    def get_create_address_url(self):
        """Return URl to redirect the user to if selected to create a new address"""
        return reverse('create_address', kwargs={'calendar_slug': self.kwargs['calendar_slug'], 'event_id': self.kwargs['event_id']})

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        return reverse('full_calendar', kwargs={'calendar_slug': calendar.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = Event.objects.get(id=self.kwargs['event_id'])
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        context['calendar'] = calendar
        context['calendar_id'] = calendar.id
        context['event'] = event

        return context


class CreateAddressView(LoginRequiredMixin, CreateView):
    """ View to handle requests to create a new address. """

    model = Address
    template_name = 'address_create.html'
    form_class = AddressForm

    def form_valid(self, form):
        """Process a valid form."""
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        event = Event.objects.get(id=self.kwargs['event_id'])

        name = form.cleaned_data.get('name')
        address1 = form.cleaned_data.get('address1')
        address2 = form.cleaned_data.get('address2')
        zip_code = form.cleaned_data.get('zip_code')
        city = form.cleaned_data.get('city')
        country = form.cleaned_data.get('country')

        address = Address.objects.create(
            name=name,
            address1=address1,
            address2=address2,
            zip_code=zip_code,
            city=city,
            country=country
        )

        event_exists = MeetingAddress.objects.filter(event=event).exists()

        if event_exists:
            meeting_address_object = MeetingAddress.objects.get(
                event=event
            )
            meeting_address_object.address = address
            meeting_address_object.save()
        else:
            meeting_address_object = MeetingAddress.objects.create(
                event=event,
                address=address
            )

        return redirect('full_calendar', calendar_slug=calendar.slug)

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return reverse('full_calendar', kwargs={'calendar_slug': self.kwargs['calendar_slug']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        context['calendar'] = calendar
        context['calendar_id'] = calendar.id
        event = Event.objects.get(id=self.kwargs['event_id'])
        context['event'] = event

        return context


class EditEventView(LoginRequiredMixin, UpdateView):
    """ View that handles event edit requests. """

    model = Event
    template_name = 'event_update.html'
    form_class = CreateEventForm
    pk_url_kwarg = "event_id"

    def form_valid(self, form):
        event = form.save()

        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        club = Club.objects.get(calendar=event.calendar)

        if club.meeting_type == 'ONL':
            return redirect('edit_event_link', calendar_slug=calendar.slug, event_id=event.id)

        if club.meeting_type == 'INP':
            return redirect('edit_event_address', calendar_slug=calendar.slug, event_id=event.id)

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return reverse('full_calendar', kwargs={'calendar_slug': self.kwargs['calendar_slug']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        context['calendar'] = calendar
        context['calendar_id'] = calendar.id
        context['calendar_name'] = calendar.name
        context['user'] = self.request.user

        return context


class EditEventLinkView(LoginRequiredMixin, UpdateView):
    """ View that handles event edit link requests. """

    model = Event
    template_name = 'event_link_update.html'
    form_class = MeetingLinkForm
    pk_url_kwarg = "event_id"

    def form_valid(self, form):
        """Process a valid form."""
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        event = Event.objects.get(id=self.kwargs['event_id'])

        meeting_link = form.cleaned_data.get('meeting_link')

        meeting_link_object = MeetingLink.objects.get(event=event)

        meeting_link_object.meeting_link = meeting_link

        meeting_link_object.save()
        return render(self.request, 'fullcalendar.html', {'calendar': event.calendar})

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return reverse('full_calendar', kwargs={'calendar_slug': self.kwargs['calendar_slug']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        event = Event.objects.get(id=self.kwargs['event_id'])
        context['calendar'] = calendar
        context['calendar_id'] = calendar.id
        context['calendar_name'] = calendar.name
        context['event_name'] = event.title
        context['user'] = self.request.user

        return context


class EditEventAddressView(LoginRequiredMixin, UpdateView):
    """ View that handles event address edit requests. """

    model = Event
    template_name = 'event_address_update.html'
    form_class = MeetingAddressForm
    pk_url_kwarg = "event_id"

    def get_form_kwargs(self):
        kwargs = super(EditEventAddressView, self).get_form_kwargs()
        kwargs['calendar_slug'] = self.kwargs['calendar_slug']
        return kwargs

    def form_valid(self, form):
        """Process a valid form."""
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        event = Event.objects.get(id=self.kwargs['event_id'])

        address = form.cleaned_data.get('address')

        meeting_address_object = MeetingAddress.objects.get(event=event)

        meeting_address_object.address = address

        meeting_address_object.save()
        return render(self.request, 'fullcalendar.html', {'calendar': event.calendar})

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return reverse('full_calendar', kwargs={'calendar_slug': self.kwargs['calendar_slug']})

    def get_create_address_url(self):
        """Return URl to redirect the user to if selected to create a new address"""
        return reverse('create_address', kwargs={'calendar_slug': self.kwargs['calendar_slug'], 'event_id': self.kwargs['event_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        event = Event.objects.get(id=self.kwargs['event_id'])
        context['calendar'] = calendar
        context['calendar_id'] = calendar.id
        context['calendar_slug'] = calendar.slug
        context['calendar_name'] = calendar.name
        context['event_name'] = event.title
        context['user'] = self.request.user

        return context


class DeleteEventView(LoginRequiredMixin, DeleteView):
    """ View that handles event delete requests. """

    model = Event
    template_name = 'event_delete.html'
    form_class = CreateEventForm
    pk_url_kwarg = "event_id"

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        return reverse('full_calendar', kwargs={'calendar_slug': calendar.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        context['calendar'] = calendar
        context['calendar_id'] = calendar.id
        context['calendar_name'] = calendar.name
        context['user'] = self.request.user

        return context


class EventDetailView(LoginRequiredMixin, DetailView):
    """ View that shows event details and links to edit and delete event functions. """

    model = Event
    template_name = 'event_detail.html'
    pk_url_kwarg = "event_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        event = Event.objects.get(id=self.kwargs['event_id'])
        context['calendar'] = calendar
        context['calendar_id'] = calendar.id
        context['calendar_slug'] = calendar.slug
        context['calendar_name'] = calendar.name
        context['event_name'] = event.title
        context['user'] = self.request.user

        return context
