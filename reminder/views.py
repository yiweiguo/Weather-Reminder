from django.shortcuts import render

def manage(request):
   zipcodes = range(10001,10010)
   return render(request, 'manage.html', {'zipcodes': zipcodes})



