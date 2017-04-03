from django.shortcuts import render, redirect
from django.contrib.auth import logout
# Create your views here.

def logout_user(request, next_pate= None):
    '''
    Log out the user
    '''
    logout(request)
    return redirect("/")
