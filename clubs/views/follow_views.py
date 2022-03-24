"""Follow related views."""
from clubs.models import User
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect


@login_required
def follow_toggle(request, user_id):
    current_user = request.user
    try:
        followee = User.objects.get(id=user_id)
        current_user.toggle_follow(followee)
    except ObjectDoesNotExist:
        return redirect('user_detail_list')
    else:
        messages.add_message(request, messages.SUCCESS, "Success!")
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        return redirect('user_detail', user_id=user_id)
