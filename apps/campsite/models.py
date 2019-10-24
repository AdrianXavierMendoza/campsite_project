from __future__ import unicode_literals
from django.db import models
import re, bcrypt

class UserManager(models.Manager):
    def validator(self, postData):
        errors = {}
        if len(postData['first_name']) < 2:
            errors['first_name'] = "First Name should be at least 2 characters"
        if len(postData['last_name']) < 2:
            errors['last_name'] = "Last Name should be at least 2 characters"
        
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        user = User.objects.filter(email = postData['email'])
        if len(user) > 0:
            errors['email'] = "There is already a user with this email address"
        if not EMAIL_REGEX.match(postData['email']):
            errors['emailvalid'] = "Invalid email address"
        
        PW_REGEX = re.compile(r"^(?=.*[a-z])")
        if len(postData['pw']) < 8:
            errors['pwlen'] = "Password must be at least 8 characters"
        if not PW_REGEX.match(postData['pw']):
            errors['pwvalid'] = "Password must contain one lowercase alphabetical character"
        if postData['confirm_pw'] != postData['pw']:
            errors['confirmpw'] = "Passwords must match"
        
        return errors

    def login_validator(self, postData):
        login_errors = {}
        logged_user = User.objects.filter(email = postData['email'])
        if len(logged_user) < 1:
            login_errors['noemail'] = "Login failed"
        else:
            if not bcrypt.checkpw(postData['pw'].encode(), logged_user[0].pw.encode()):
                login_errors['pwinvalid'] = "Login failed"
        return login_errors

class User(models.Model):
    first_name = models.CharField(max_length = 255)
    last_name = models.CharField(max_length = 255)
    email = models.CharField(max_length = 255)
    pw = models.CharField(max_length = 255)
    confirm_pw = models.CharField(max_length = 255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

class Campground(models.Model):
    name = models.CharField(max_length = 255)
    contractCode = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Reservation(models.Model):
    user = models.ForeignKey(User, related_name = "reservations")
    campground = models.ForeignKey(Campground, related_name = "reservations")
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Review(models.Model):
    campground = models.ForeignKey(Campground, related_name = "reviews")
    user = models.ForeignKey(User, related_name = "reviews")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)