from django.shortcuts import render, HttpResponse, redirect
from .models import *
from django.contrib import messages
import bcrypt



#renders index
def index(request):
    return render(request, "campsite/index.html")

#renders login_page
def login_page(request):
    return render(request, "campsite/register_login.html")

#registration process (clicking button to submit the form)
def registration(request):
    errors = User.objects.validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/login_page')
    else:
        password = request.POST['pw']
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        new_user = User.objects.create(
            first_name = request.POST['first_name'],
            last_name = request.POST['last_name'],
            email = request.POST['email'],
            pw = pw_hash)
        request.session['id'] = new_user.id
        return redirect(f"/new_user/{new_user.id}")

#login process
def login(request):
    login_errors = User.objects.login_validator(request.POST)
    if len(login_errors) > 0:
        for key, value in login_errors.items():
            messages.error(request, value)
        return redirect('/login_page') 
    else:
        logged_user = User.objects.get(email = request.POST['email'])
        request.session['id'] = logged_user.id
        return redirect(f"/new_user/{logged_user.id}")
    
#renders success page
def success(request, id):
    if 'id' not in request.session:
        return redirect("/")
    else:
        context = {
            "user":User.objects.get(id=id)
        }
        return render(request, "campsite/success.html", context)

def logout(request):
    request.session.clear()
    return redirect("/")

def edit(request):
    return render (request, "campsite/edit.html")





    


