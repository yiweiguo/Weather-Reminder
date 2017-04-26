import urllib2, urllib, json, traceback
from collections import defaultdict
from datetime import date, datetime
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.core.mail import EmailMessage
from models import Reminder

def manage(request):
   user_id = None
   if request.user.is_authenticated():
       user_id = request.user.id
   else:
       return HttpResponseRedirect("/admin/login/")
   reminders = Reminder.objects.filter(user_id=user_id)
   return render(request, 'manage.html', {'reminders': reminders})

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



