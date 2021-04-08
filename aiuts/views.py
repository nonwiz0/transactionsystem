from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.template import loader
from django.views import generic
from .models import User, Transaction
from django.utils import timezone
import hashlib
from random import random
from django.contrib import messages

class IndexView(generic.ListView):
    template_name = 'aiuts/index.html'
    context_object_name = 'all_user'

    def get_queryset(self):
        """Return the last five published questions."""
        return User.objects.all()[:]

class LoginView(generic.TemplateView):
    template_name = 'aiuts/login.html'

class SignupView(generic.TemplateView):
    template_name = 'aiuts/sign_up.html'

class GetbalanceView(generic.TemplateView):
    template_name = 'aiuts/get_balance.html'

class GetaccidView(generic.TemplateView):
    template_name = 'aiuts/get_acc_id.html'

def create_acc(request):
    fullname = request.POST['fullname']
    password = request.POST['password']
     
    if not len(fullname) or not len(password):
        messages.info(request, 'Provide appropriate your full name and password!')
        return HttpResponseRedirect(reverse('aiuts:signup'))

    acc_id = hashlib.md5(str.encode(fullname)).hexdigest()
    hash_pw = hashlib.md5(str.encode(password)).hexdigest()
    for acc in User.objects.all():
        if acc.acc_id == acc_id:
            messages.info(request, 'This name is already registered once!')
            return HttpResponseRedirect(reverse('aiuts:signup'))
    new_acc = User(acc_id, hash_pw, random() * 100)    
    new_acc.save()
    messages.info(request, '{} has been created!'.format(new_acc.acc_id))
    return HttpResponseRedirect(reverse('aiuts:index'))

def check_balance(request):
    acc_id = request.POST['acc_id']
    password = request.POST['password']
    if not len(acc_id) or not len(password):
        messages.info(request, 'Acc_id or password is not filled properly')
        return HttpResponseRedirect(reverse('aiuts:getbalance'))
    hash_pw = hashlib.md5(str.encode(password)).hexdigest()
    if User.objects.filter(pk=acc_id).exists():
        curr_user = User.objects.get(pk=acc_id)
        if curr_user.password == hash_pw:
            messages.info(request, 'Your account has {:.2f} Baht'.format(curr_user.balance))
            return HttpResponseRedirect(reverse('aiuts:getbalance'))
    else:
        messages.info(request, 'Incorrect acc id or password!')
        return HttpResponseRedirect(reverse('aiuts:getbalance'))



def check_accid(request):
    fullname = request.POST['fullname']
    password = request.POST['password']
    hash_acc = hashlib.md5(str.encode(fullname)).hexdigest()
    hash_pw = hashlib.md5(str.encode(password)).hexdigest()
    for acc in User.objects.all():
        if acc.acc_id == hash_acc and acc.password == hash_pw:
            messages.info(request, 'Acc ID: {}'.format(acc.acc_id))
            return redirect(request.META['HTTP_REFERER'])
        if acc.acc_id == hash_acc and acc.password != hash_pw:
            messages.info(request, 'Incorrect credential')
            return redirect(request.META['HTTP_REFERER'])

def check_account(request):
    acc_id = request.POST['acc_id']
    password = request.POST['password']
    hash_pw = hashlib.md5(str.encode(password)).hexdigest()
    for acc in User.objects.all():
        if acc.acc_id == acc_id and acc.password == hash_pw:
            template = loader.get_template('aiuts/account_dash.html')
            user = User.objects.get(pk=acc_id)
            context = {'user': user}
            messages.info(request, 'Login successfully')
            return HttpResponse(template.render(context, request))
    messages.info(request, 'Incorrect credential')
    return HttpResponseRedirect(reverse('aiuts:login'))


def send_money(request):
    acc_id = request.POST['source']
    recipient = request.POST['destination'].strip()
    amount = float(request.POST['amount'])
    password = request.POST['password']
    hash_pw = hashlib.md5(str.encode(password)).hexdigest()
    remark = request.POST['remark'] 
    if not len(acc_id) or not len(recipient) or not len(password) or amount < 0.0 or acc_id == recipient:
        messages.info(request, "Please double check the information again to send the money")
        return HttpResponseRedirect(reverse('aiuts:sendmoneypage'))
    if not User.objects.filter(pk=acc_id).exists() or not User.objects.filter(pk=recipient).exists():
        messages.info(request, "please double check the detail again")
        return HttpResponseRedirect(reverse('aiuts:sendmoneypage'))
    acc = User.objects.get(pk=acc_id)
    rec_user = User.objects.get(pk=recipient)
    if acc.password == hash_pw:
        if rec_user.balance > amount:
            acc.balance -= amount
            rec_user.balance += amount
            rec_user.save()
            acc.save()
            transaction = Transaction(sender=acc, recipient=rec_user, amount=amount, remark=remark)
            transaction.save()     
            messages.info(request, "You have sent {:.2f} baht to {}".format(amount, rec_user.acc_id))
            return HttpResponseRedirect(reverse('aiuts:sendmoneypage')) 
    messages.info(request, "Sent failed, please double check the detail again")
    return HttpResponseRedirect(reverse('aiuts:sendmoneypage')) 

def deposit_money(request):
    acc_id = request.POST['acc_id']
    amount = float(request.POST['amount'])
    password = request.POST['password']
    hash_pass = hashlib.md5(str.encode(password)).hexdigest()
    if User.objects.filter(pk=acc_id).exists():
        user_acc = User.objects.get(pk=acc_id)
        if hash_pass == user_acc.password:
            user_acc.balance += amount
            user_acc.save()
            record = Transaction(sender=user_acc, recipient=user_acc, amount=amount, remark="Deposit")
            record.save()
            messages.info(request, "Your balance right now is {:.2f}".format(user_acc.balance))
            return redirect(request.META['HTTP_REFERER'])

class TransactionView(generic.TemplateView):
    template_name = 'aiuts/get_summary_with_acc.html'

class SendMoneyView(generic.TemplateView):
    template_name = 'aiuts/send_money.html'


def get_summary_of_transaction(request):
    acc_id = request.POST['acc_id']
    password = request.POST['password']
    hash_pass = hashlib.md5(str.encode(password)).hexdigest()
    template = loader.get_template('aiuts/get_summary.html')
    if User.objects.filter(pk=acc_id).exists():
        user_acc = User.objects.get(pk=acc_id)
        if hash_pass == user_acc.password:
            all_transaction = list(Transaction.objects.filter(sender=acc_id))+list(Transaction.objects.filter(recipient=acc_id)[:])
            context = {
                'all_transaction': all_transaction,
                'user': acc_id
            }
            return HttpResponse(template.render(context, request))
    messages.info(request, "Incorrect password!")
    return redirect(request.META['HTTP_REFERER'])

