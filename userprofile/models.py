from django.db import models
from django.contrib.auth import get_user_model
User=get_user_model()
gender = (
    ("male","male"),
    ("female","female"),
)
# Create your models here.
class userprofile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    gender = models.CharField(choices=gender,max_length=10)
    number = models.CharField(max_length=10,null=True)
    email = models.EmailField(max_length=254,null=True)
    caloriegoal = models.CharField(max_length=100,default='3000')


    def __str__(self):
        return self.name