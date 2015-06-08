from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url='/accounts/google/login')
def show(request):
    print("question:show")
    pass
