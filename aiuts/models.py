from django.db import models
from django.contrib.auth.models import User
import hashlib
# Create your models here.


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    acc_id = models.CharField(max_length=256, primary_key=True)
    balance = models.FloatField(default=0.01)
    
    def __str__(self):
        return "{}".format(self.acc_id)

class Transaction(models.Model):
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='sender')
    recipient = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='recipient')
    amount = models.FloatField(null=False, blank=False)
    remark = models.CharField(max_length=256, default="No message")
    record_date = models.DateTimeField('date recorded', auto_now_add=True)
    complete = models.BooleanField(default=False)
    type = models.CharField(choices=[('Top Up', 'TU'), ('Request of Payment', 'ROP'), ('Normal Transaction', 'NOR')], default='Normal Transaction', max_length=20)
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return "Sender: {}, Recipient: {}, Amount: {}, Date: {}, Remark: {}".format(self.sender, self.recipient, self.amount, self.record_date, self.remark)
  
# class Pending(models.Model):
#     Transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
#     Transaction_choices = [ ('TU','Top Up'), ('ROP','Request of Payment')]
#     Type = models.CharField(
#         choices = Transaction_choices,
#         default = "Not fill",
#         max_length = 256
#     )
#     Complete_status = models.BooleanField(default=False)
