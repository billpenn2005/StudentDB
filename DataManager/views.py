from django.shortcuts import render
from django import http
from django.shortcuts import redirect
from django.urls import reverse
from django.template import loader



# Create your views here.

def IndexPage(request):
    if request.session.get('is_login') != True:
        return http.HttpResponseRedirect(reverse('Auth:login'))
    template=loader.get_template('main_index.html')
    return http.HttpResponse(template.render(context=None,request=request))