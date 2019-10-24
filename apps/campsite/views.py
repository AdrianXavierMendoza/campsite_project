from django.shortcuts import render, HttpResponse, redirect
from .models import *
from django.contrib import messages
import bcrypt
import xmltodict
import requests



#renders index (homepage)
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
        return render(request, "campsite/profile.html", context)
#submits log out and ends session
def logout(request):
    request.session.clear()
    return redirect("/")

#renders user profile
def profile(request):
    return render(request, "campsite/profile.html")

#renders edit page
def edit(request):
    return render (request, "campsite/edit.html")

#renders search page
def search(request):
   
        # context = {
        #     "site" : request.session['search_result'],
        #     # "site_photo" : request.session['result_photo'],
        #     "site_lat" : request.session['result_lat'],
        #     "site_lon" : request.session['result_lon'],
        #     # "site_pets" : request.session['spotlight_pets']
        # }
    return render(request, "campsite/search_sites.html")
 
#takes in parameters and redirects to search page (possibly needs AJAX)
def search_results(request):
    # if "pstate" in request.GET:
    park_state = request.GET['pstate']
    park_amenity = request.GET['amenity']
    park_site_type = request.GET['siteType']
    park_pet = request.GET['petsAllowed']
    r = requests.get("http://api.amp.active.com/camping/campgrounds?pstate="+park_state+park_amenity+park_site_type+park_pet+"&api_key=axg5nzjhbug58fg67rfgwspc")
    obj = xmltodict.parse(r.text)
    print(obj['resultset'])


    for camp in obj['resultset']['result']:
        camp['contract_Code'] = camp['@contractID']
        camp['park_Id'] = camp['@facilityID']
        camp['facilityName'] = camp['@facilityName']
        camp['facilityPhoto'] = camp['@faciltyPhoto']
        camp['latitude'] = round(float(camp['@latitude']))
        camp['longitude'] = round(float(camp['@longitude']))
        # camp['amenity'] = park_amenity
    context = {
        "campsites" : obj['resultset']['result'],
        
    }
    return render(request, "campsite/search_sites.html", context)

#renders reservation page
def reservation(request, park_Id, contract_Code):
    r = requests.get("http://api.amp.active.com/camping/campground/details?parkId="+park_Id+"&contractCode="+contract_Code+"&api_key=axg5nzjhbug58fg67rfgwspc")
    obj = xmltodict.parse(r.text)
    for camp in obj['detailDescription']['photo']:
        camp['photos'] = camp['@realUrl']

    context = {
        "site_name" : obj['detailDescription']['@facility'],
        "site_desc" : obj['detailDescription']['@description'],
        "site_img" : obj['detailDescription']['photo'][0]['@realUrl'],
        "site_other_img" :  obj['detailDescription']['photo'],
        "site" : obj['detailDescription'],
        
    }
    return render(request, "campsite/reservation.html", context)



#renders confirmation page 
def confirmation(request):
    return render(request, "campsite/confirmation.html")


