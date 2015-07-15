from django.shortcuts import render_to_response, redirect, render
from django.contrib.auth import login as auth_login, authenticate
from django.contrib import messages
from .forms import User_form, UserProfile_form

# Create your views here.
def signup(request):
    if request.method == 'GET':
        return render(request, 'account/signup.html', {'user_form': User_form(), 'userprofile_form': UserProfile_form()})
    if request.method == 'POST':
        user_form = User_form(request.POST)
        userprofile_form = UserProfile_form(request.POST, request.FILES)
        if user_form.is_valid() and userprofile_form.is_valid():
            user = user_form.save()
            userprofile = userprofile_form.save(commit=False)
            userprofile.user = user
            userprofile.save()
            return redirect('/accounts/login/')
        return render(request, 'account/signup.html', {'user_form': user_form, 'userprofile_form': userprofile_form})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request,user)
                return redirect('/dotchain')
            else:
                messages.error(request, 'このユーザは使用できません。')
        else:
            messages.error(request, '正しいユーザ名・パスワードを入力してください。')
    return render(request, 'account/login.html')
