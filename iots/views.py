from django.shortcuts import render
from iots import models
from api import calendar, weather
from auth import social_user
from worker import mydb
import inspect

def index(request):
    #you can get request.user
    context = mydb.view_sensor_dict()

    if not request.user.is_anonymous:
        token = social_user.get_token('refresh_token', request.user)
        calendar.insert_event(token)
        calendar_service = calendar.get_event(token)
        context["email"] = mydb.view_email_dict(request.user.email)
        context["master"] = request.user.email
        context["weather"] = weather.get_weather()

    return render(request, 'index.html', context)
