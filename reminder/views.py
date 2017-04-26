import urllib2, urllib, json, traceback
from collections import defaultdict
from datetime import date, datetime
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.core.mail import EmailMessage
from models import Reminder
from forms import AddReminderForm


def manage(request):
    user_id = None
    if request.user.is_authenticated():
        user_id = request.user.id
    else:
        return HttpResponseRedirect("/admin/login/")
    if request.method == 'POST':
        post_form = AddReminderForm(request.POST)
        if post_form.is_valid():
            zipcode = post_form.cleaned_data['zipcode']
            reminder = post_form.cleaned_data['reminder']
            Reminder.objects.create(user_id=user_id, zipcode=zipcode, warning_event=reminder)
    reminders = Reminder.objects.filter(user_id=user_id)
    form = AddReminderForm()
    return render(request, 'manage.html', {'form': form, 'reminders': reminders, 'logged_in': True})


def del_reminder(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/admin/login/")
    try:
        reminder_id = int(request.GET.get('id', ''))
        p = Reminder.objects.get(id=int(reminder_id))
        p.delete()
    except:
        pass
    return HttpResponseRedirect("/")


def get_weather(zipcode):
    appid = '1fea7992fc6d1c345747f3fb6a9dfde7'  # replace with your own API key
    baseurl = 'http://api.openweathermap.org/data/2.5/forecast/daily?zip=%s&APPID=%s&cnt=2&units=imperial'
    actual_url = baseurl % (zipcode, appid)
    data = dict()
    try:
        result = urllib2.urlopen(actual_url).read()
        data = json.loads(result)
    except:
        print(traceback.format_exc())
    return data


def generate_weather_string(data):
    return "The weather condition will be %s in %s on %s. The temperature will be %s to %s F." % (
        data['list'][1]['weather'][0]['main'],
        data['city']['name'],
        datetime.fromtimestamp(data['list'][1]['dt']).strftime('%m/%d/%Y'),
        data['list'][1]['temp']['min'],
        data['list'][1]['temp']['max'],
    )


def test_email(request):
    user_id = None
    if request.user.is_authenticated():
        user_id = request.user.id
    else:
        return HttpResponseRedirect("/admin/login/")
    reminders = Reminder.objects.filter(user_id=user_id)
    # De-duplicate zipcode.
    zipcodes = set()
    for reminder in reminders:
        zipcodes.add(reminder.zipcode)
    body = "Dear %s,\n\n" % request.user.username
    for zipcode in zipcodes:
        body += generate_weather_string(get_weather(zipcode)) + "\n"
    body += "\nBest,\nWeather Reminder"
    message = EmailMessage("Weather Report", body, to=[request.user.email])
    message.send()
    return HttpResponseRedirect("/")
