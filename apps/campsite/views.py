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
        return redirect("/profile")

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
        return redirect("/profile")
    
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
    context={
        "current_user": User.objects.get(id=request.session['id'])
    }
    return render(request, "campsite/profile.html", context)

#renders edit page
def edit(request, reso_id):
    # reso = Reservation.objects.get(id=reso_id)
    context = {
        "reso_edit" : Reservation.objects.get(id=reso_id),
        # "start" : reso.start_date.strftime('%m-%d-%Y'),
    }
    return render (request, "campsite/edit.html", context)

def update(requests, reso_id):
    update_reso = Reservation.objects.get(id=reso_id)
    update_reso.start_date = requests.POST['start_date']
    update_reso.end_date = requests.POST['end_date']
    update_reso.save()
    return redirect('/profile')

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
        # camp['latitude'] = round(float(camp['@latitude']))
        # camp['longitude'] = round(float(camp['@longitude']))
        # camp['amenity'] = park_amenity
    context = {
        "campsites" : obj['resultset']['result'],
        
    }
    return render(request, "campsite/search_sites.html", context)

#renders reservation page
def reservation(request, park_Id, contract_Code):
    
    r = requests.get("http://api.amp.active.com/camping/campground/details?parkId="+park_Id+"&contractCode="+contract_Code+"&api_key=axg5nzjhbug58fg67rfgwspc")
    obj = xmltodict.parse(r.text)

    lat = obj['detailDescription']['@latitude']
    lon = obj['detailDescription']['@longitude']
    w = requests.get("http://api.openweathermap.org/data/2.5/weather?lat="+lat+"&lon="+lon+"&appid=366b23b0c77d79243f8e76a681d058eb&mode=xml")
    weather = xmltodict.parse(w.text)
    # if obj['detailDescription']['photo']:
    for camp in obj['detailDescription']['photo']:
        camp['photos'] = camp['@realUrl']
    if not Campground.objects.filter(park_id = park_Id).first():
        Campground.objects.create(name=obj['detailDescription']['@facility'], park_id=obj['detailDescription']['@facilityID'])
    print(Campground.objects.all())
    context = {
        "site" : obj['detailDescription'],
        "site_name" : obj['detailDescription']['@facility'],
        "site_desc" : obj['detailDescription']['@description'],
        "site_img" : obj['detailDescription']['photo'][0]['@realUrl'],
        "site_other_img" :  obj['detailDescription']['photo'],
        "site_directions" : obj['detailDescription']['@drivingDirection'],
        "site_url" : obj['detailDescription']['@fullReservationUrl'],
        "site_address" : obj['detailDescription']['address']['@streetAddress'],
        "site_city" : obj['detailDescription']['address']['@city'],
        "site_state" : obj['detailDescription']['address']['@state'],
        "site_zip" : obj['detailDescription']['address']['@zip'],
        "site_info" : obj['detailDescription']['@importantInformation'],
        

        "site_lat" : obj['detailDescription']['@latitude'],
        "site_lon" : obj['detailDescription']['@longitude'],


        "weather_city" : weather['current']['city']['@name'],
        "weather_temp": round((float(weather['current']['temperature']['@value']) - 273.15)*(9/5)+32),
        "weather_clouds" : weather['current']['weather']['@value'],
        "weather_rain" : weather['current']['precipitation']['@mode'],
        "weather_hum": weather['current']['humidity']['@value'],
        "weather_all": weather['current'],
        "contract_Code": contract_Code,
        "park_Id": park_Id,
        "all_reviews": Review.objects.filter(campground=Campground.objects.get(park_id = park_Id))
    }
    return render(request, "campsite/reservation.html", context)

#renders confirmation page 
def confirmation(request, reso_id):
    context = {
        "reso": Reservation.objects.get(id=reso_id),
    }
    return render(request, "campsite/confirmation.html", context)

def post_review(request, park_Id):
    user = User.objects.get(id=request.session['id'])
    campground = Campground.objects.filter(park_id=park_Id).first()
    Review.objects.create(content=request.POST['content'], user=user, campground=campground)
    contract_code = request.POST['post_review']
    return redirect(f'/reservation/{park_Id}/{contract_code}')

def make_reso(request, park_Id):
    user = User.objects.get(id=request.session['id'])
    campground = Campground.objects.filter(park_id=park_Id).first()
    new_reso = Reservation.objects.create(user=user, campground=campground, start_date=request.POST['start_date'], end_date=request.POST['end_date'])
    reso_id = new_reso.id
    return redirect(f'/confirmation/{reso_id}')

def cancel(request, reso_id):
    c= Reservation.objects.get(id=reso_id)
    c.delete()

    return redirect('/profile')