from django.db import models
from django.utils import timezone
import datetime
# Create your models here.

class User(models.Model):
    acc_id = models.CharField(max_length=256, primary_key=True)
    password = models.CharField(max_length=256)
    balance = models.FloatField(default=0.01)


class Transaction(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient')
    amount = models.FloatField()
    remark = models.CharField(max_length=256, default="No message")
    record_date = models.DateTimeField('date recorded', auto_now_add=True)
    id = models.AutoField(primary_key=True)

