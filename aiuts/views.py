from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.template import loader
from django.views import generic
from django.contrib.auth.models import User
from .models import Account, Transaction
from django.utils import timezone
import hashlib
from random import random
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate
from datetime import datetime

class IndexView(generic.ListView):
    template_name = 'aiuts/index.html'
    context_object_name = 'all_user'

    def get_queryset(self):
        """Return the last five published questions."""
        return Account.objects.all()[:]

class LoginView(generic.TemplateView):
    template_name = 'aiuts/login.html'

class SignupView(generic.TemplateView):
    template_name = 'aiuts/sign_up.html'

class Dashboard(LoginRequiredMixin, generic.ListView):
    login_url = '/accounts/login'
    template_name = 'aiuts/account_dash.html'
    model = Transaction

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Account.objects.get(user=self.request.user)
        return context

class TransactionSummary(LoginRequiredMixin, generic.ListView):
    login_url = '/accounts/login'
    template_name = 'aiuts/get_summary.html'
    context_object_name = 'user'

    def get_queryset(self):
        curr_user = Account.objects.get(user=self.request.user)
        acc_id = curr_user.acc_id
        return acc_id

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curr_user = Account.objects.get(user=self.request.user)
        acc_id = curr_user.acc_id
        context['all_transaction'] = set(Transaction.objects.filter(sender=curr_user)).union(set(Transaction.objects.filter(recipient=curr_user)[:]))
        return context

def create_acc(request):
    username = request.POST['username']
    password = request.POST['password']
    if not len(username) or not len(password):
        messages.info(request, 'Provide appropriate your full name and password!')
        return HttpResponseRedirect(reverse('aiuts:signup'))
    acc_id = hashlib.md5(str.encode(username)).hexdigest()
    user = User.objects.create_user(username=username, password=password)
    user.save()
    account = Account(user=user, acc_id=acc_id, balance=random() * 100)
    account.save()
    messages.info(request, '{} has been created!'.format(acc_id))
    return HttpResponseRedirect(reverse('aiuts:index'))


def send_money(request):
    acc_id = request.POST['source']
    recipient = request.POST['destination'].strip()
    amount = float(request.POST['amount'])
    password = request.POST['password']
    remark = request.POST['remark'] 
    if Account.objects.filter(acc_id=recipient).exists():
        rec_acc = Account.objects.get(acc_id=recipient)
        user = authenticate(request, username=request.user.username, password=password)
        if user is not None:
            curr_acc = Account.objects.get(acc_id=acc_id)
            if amount > 0 and amount < curr_acc.balance:
                curr_acc.balance -= amount
                rec_acc.balance += amount
                curr_acc.save()
                rec_acc.save()
                transaction = Transaction(sender=curr_acc, recipient=rec_acc, amount=amount, remark=remark)
                transaction.save()     
                messages.info(request, "You have sent {:.2f} baht to {}".format(amount, rec_acc.acc_id))
                return redirect(request.META['HTTP_REFERER'])
    messages.info(request, "Please double check the detail again")
    return redirect(request.META['HTTP_REFERER'])

def deposit_money(request):
    acc_id = request.POST['acc_id']
    amount = float(request.POST['amount'])
    password = request.POST['password']
    user = authenticate(request, username=request.user.username, password=password)
    if amount > 0:
        if user is not None:
            curr_acc = Account.objects.get(user=request.user)
            curr_acc.balance += amount
            curr_acc.save()
            trans_record = Transaction(sender=curr_acc, recipient=curr_acc, amount=amount, remark="Deposit money")
            trans_record.save()
            messages.info(request, "You have deposited {:.2f} Baht".format(amount))
            return redirect(request.META['HTTP_REFERER'])
    messages.info(request, "Check the detail again before deposit!")
    return redirect(request.META['HTTP_REFERER'])
   
# def get_summary_of_transaction(request):
#     password = request.POST['password']
#     template = loader.get_template('aiuts/get_summary.html')
#     if Account.objects.filter(user=request.user).exists():
#         user_acc = Account.objects.get(user=request.user)
#         user = authenticate(request, username=request.user.username, password=password)
#         if user is not None:
#             all_transaction = set(Transaction.objects.filter(sender=user_acc.acc_id)).union(set(Transaction.objects.filter(recipient=user_acc.acc_id)[:]))
#             context = {
#                 'all_transaction': all_transaction,
#                 'user': user_acc.acc_id,
#                 'password': password
#             }
#             return HttpResponse(template.render(context, request))
#     messages.info(request, "Incorrect password!")
#     return redirect(request.META['HTTP_REFERER'])

def search_transaction(request):
    template = loader.get_template('aiuts/get_summary.html')
    user_acc = Account.objects.get(user=request.user)
    acc_addr = request.POST['acc_addr']
    t = set(Transaction.objects.filter(sender=user_acc.acc_id)).union(set(Transaction.objects.filter(recipient=user_acc.acc_id)[:]))
    found_record = []
    from_date = request.POST['from_date']
    to_date = request.POST['to_date']
    if len(acc_addr):
        for i in t:
            if i.sender.acc_id == acc_addr or i.recipient.acc_id == acc_addr:
                found_record.append(i)

    if len(from_date) and len(to_date):
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
        for i in t:
            temp = i.record_date.date()
            if temp >= from_date_obj and temp <= to_date_obj:
                found_record.append(i)

    all_transaction = set(Transaction.objects.filter(sender=user_acc.acc_id)).union(set(Transaction.objects.filter(recipient=user_acc.acc_id)[:]))
    context = {'all_transaction':found_record, "user":user_acc.acc_id}
    messages.info(request, "Found Record: {}".format(found_record))
    return HttpResponse(template.render(context, request))
