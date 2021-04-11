from django.db import models
from django.contrib.auth.models import User
import hashlib
# Create your models here.


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    acc_id = models.CharField(max_length=256, primary_key=True)
    balance = models.FloatField(default=0.01)


class Transaction(models.Model):
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='sender')
    recipient = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='recipient')
    amount = models.FloatField()
    remark = models.CharField(max_length=256, default="No message")
    record_date = models.DateTimeField('date recorded', auto_now_add=True)
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return "Sender: {}, Recipient: {}, Amount: {}, Date: {}, Remark: {}".format(self.sender, self.recipient, self.amount, self.record_date, self.remark)
  
