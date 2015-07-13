from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth import login, authenticate
from django.contrib import messages

# Create your views here.
def signup(request):
    return render_to_response('account/signup.html', context_instance=RequestContext(request))

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/dotchain')
            else:
                messages.error(request, 'このユーザは使用できません')
        else:
            messages.error(request, '正しいユーザ名・パスワードを入力してください')
    return render_to_response('account/login.html', context_instance=RequestContext(request))
