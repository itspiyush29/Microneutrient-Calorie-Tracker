from django.shortcuts import render,redirect
from .models import Food,Consume
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from userprofile.models import userprofile
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import date

# for chart
import json
from urllib.parse import quote

# Create your views here.

def signup(request):
    if request.method=="POST":
        name = request.POST['name']
        username = request.POST['username']
        email = request.POST['email']
        number = request.POST['number']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        gender = request.POST['gender']
        print(gender)

        if User.objects.filter(username=username):
            messages.error(request,"username already exist! Please try some other username")
            return redirect('signup')

        if len(username)>10:
            messages.error(request,"Username must be under 10 characters")

        if not username.isalnum():
            messages.error(request,"Username must be alphaneumeric")
        
        if User.objects.filter(email=email):
            messages.error(request,"Email already Exists")
            return redirect('login')
        
        if pass1!=pass2:
            messages.error(request,"Passwords did'nt match!")
            return redirect('signup')

        new_user = User.objects.create_user(username,email,pass1)
        new_user.save()
        user_profile = userprofile(
            user = new_user,
            name = name,
            username = username,
            gender = gender,
            number = number,
            email = email,
        )
        user_profile.save()
        if new_user is not None:
            messages.success(request,"Your account has been successfully created")
            return redirect('login')
    return render(request,'myapp/signup.html')


def login_user(request):
    if request.method=="POST":
        username=request.POST['username']
        pass1=request.POST['password']
        # returns none and not none object. Checks if credential matches with previous username and password or not.
        user1 = authenticate(username=username,password=pass1)

        if user1 is not None:
            login(request,user1)
            messages.success(request,"You are successfully Logged In.")
            return redirect('dashboard')
        else:
            messages.error(request,"Bad credentials")
            return redirect('login')
    return render(request,'myapp/login.html')

def dashboard(request):
    user1=userprofile.objects.get(user=request.user)
    consumed_food = Consume.objects.filter(user=request.user)
    if request.POST.get('CONSUME')=="consumeitem":
        food_consumed = request.POST['food_consumed']
        foodOb = Food.objects.get(name=food_consumed)
        user = request.user
        consume = Consume(user=user,food_consumed=foodOb)
        consume.save()
        foods = Food.objects.all()
    elif request.POST.get('ADD')=="additem":
        Fname = request.POST['FoodName']
        Fcarbs = request.POST['FoodCarbs']
        Fprotein = request.POST['FoodProtein']
        Ffats = request.POST['FoodFats']
        Fcalories = request.POST['FoodCalories']
        newfood = Food(name=Fname,carbs=Fcarbs,protein=Fprotein,fats=Ffats,calories=Fcalories)
        newfood.save()
        foods = Food.objects.all()
    elif request.POST.get('EMAIL')=="sendmail":
        print(user1.email)
        subject='Your Daily Statistics'
        to=str(user1.email)
        from_email='CALORIE TRACKER <jmitknowledge@gmail.com>'
        foods = Food.objects.all()
        today = date.today()
        Date = today.strftime("%B %d, %Y")
        proteins=0
        carbs=0
        fats=0
        calories=0
        for c in consumed_food:
            proteins+=c.food_consumed.protein
            carbs+=c.food_consumed.carbs
            fats+=c.food_consumed.fats
            calories+=c.food_consumed.calories
        total=carbs+proteins+fats
        carbsp=round((carbs / total) * 100)
        proteinsp=round((proteins / total) * 100)
        fatsp=round((fats / total) * 100)

        # for chart
        chart = {
            'type': 'doughnut',
            'data': {
                'datasets': [{
                'label': 'Macroneutrients',
                'data': [carbsp, proteinsp, fatsp],
                'backgroundColor': [
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(255, 206, 86, 0.5)',
                ],
                'borderColor': [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 206, 86, 1)',
                ],
                'borderWidth': 1
                }]
            }
        }
        encoded_config = quote(json.dumps(chart))
        chart_url = f'https://quickchart.io/chart?c={encoded_config}'
        d={
            'foods':foods,
            'consumed_food':consumed_food,
            'user':user1,
            'date':Date,
            'proteins':proteins,
            'carbs':carbs,
            'fats':fats,
            'calories':calories,
            'proteinsp':proteinsp,
            'carbsp':carbsp,
            'fatsp':fatsp,
            'chart_url':chart_url,
        }
        TextBody=render_to_string('email.txt',d)
        HtmlBody=render_to_string('email.html',d)
        msg=EmailMultiAlternatives(subject,TextBody,from_email,[to])
        msg.attach_alternative(HtmlBody,'text/html')
        msg.send()

        messages.success(request,"Mail sent successfully.")
        messages.info(request,"Check your mail inbox.")
        return redirect('/dashboard')
    else:    
        foods = Food.objects.all()
    return render(request,'myapp/dashboard.html',{'foods':foods,'consumed_food':consumed_food,'user':user1})

def index(request):
    return render(request,'myapp/index.html')

@login_required
def delete_consume(request,id):
    consumed_food = Consume.objects.get(id=id)
    consumed_food.delete()
    return redirect('/dashboard')


@login_required
def logout_user(request):
    logout(request)
    messages.success(request,"You have been logged out successfully!")
    return redirect('/')