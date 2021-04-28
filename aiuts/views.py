from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.template import loader
from django.views import generic
from django.contrib.auth.models import User
from .models import Account, Transaction
from django.utils import timezone
from random import random
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate
from datetime import datetime, timedelta
import hashlib
from django.http import JsonResponse
from django.core import serializers
from .forms import TopupForm

class TopupView(LoginRequiredMixin, generic.CreateView):
    login_url = '/accounts/login'
    form_class = TopupForm
    template_name = "aiuts/top_up.html"

    def get(self, *args, **kwargs):
        acc = Account.objects.filter(user=self.request.user)
        form = self.form_class(account=acc)
        curr_acc = Account.objects.get(user=self.request.user)
        transactions = set(Transaction.objects.filter(complete=False).filter(sender=curr_acc)).union(set(Transaction.objects.filter(complete=False).filter(recipient=curr_acc)))
        context = {"form": form, "all_transaction": transactions,
                   "user":curr_acc,
                   "bank": Account.objects.get(acc_id="bd5af1f610a12434c9128e4a399cef8a")}
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        if self.request.is_ajax and self.request.method == "POST":
            form = self.form_class(self.request.POST)
            if form.is_valid():
                instance = form.save()
                ser_instance = serializers.serialize('json', [instance,])
                return JsonResponse({"instance": ser_instance}, status=200)
            else:
                return JsonResponse({"error":""}, status=400)

def checkTopupReq(request):
    if request.is_ajax and request.method == "GET":
        return JsonResponse({"valid": True}, status=200)

def getRandomData(request):
    # request should be ajax and method should be GET.
    if request.is_ajax and request.method == "GET":
        now = str(timezone.now())
        return JsonResponse({"randomdata":str(hashlib.md5(now.encode()))+" - "+now}, status = 200)
    return JsonResponse({}, status = 400)

class IndexView(generic.ListView):
    template_name = 'aiuts/index.html'
    context_object_name = 'all_user'
    
    def get_queryset(self):
        """Return the last five published questions."""
        return Account.objects.all()[:]

class SignupView(generic.TemplateView):
    template_name = 'aiuts/sign_up.html'


class AdminDashboard(LoginRequiredMixin, generic.ListView):
    login_url = '/accounts/login'
    template_name = 'aiuts/admin_dash.html'
    model = Transaction
    context_object_name = 'all_transaction'

    def get_queryset(self):
        return Transaction.objects.filter(complete=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Account.objects.get(user=self.request.user)
        return context
    

class Dashboard(LoginRequiredMixin, generic.ListView):
    login_url = '/accounts/login'
    template_name = 'aiuts/account_dash.html'
    model = Transaction
    context_object_name = 'all_transaction'

    def get_queryset(self):
        curr_acc = Account.objects.get(user=self.request.user)
        return set(Transaction.objects.filter(complete=False).filter(sender=curr_acc)).union(set(Transaction.objects.filter(complete=False).filter(recipient=curr_acc)))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Account.objects.get(user=self.request.user)
        return context
    
    def post(self, request, *args, **kwargs):
        template = loader.get_template(self.template_name)
        user_acc = Account.objects.get(user=request.user)
        amount = float(request.POST['amount'])
        sender_addr = request.POST['acc_addr']
        if amount < 0:
            messages.info(request, "Please enter appropriate amount")
            return redirect(request.META['HTTP_REFERER'])
        if len(sender_addr):
            sender = Account.objects.get(acc_id = sender_addr)
            req_user = Transaction(sender=sender, recipient=user_acc, amount=amount, type="Request of Payment")
            req_user.save()
        messages.info(request, "New pending request is created!")
        return redirect(request.META['HTTP_REFERER'])

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

    def post(self, request, *args, **kwargs):
        template = loader.get_template(self.template_name)
        user_acc = Account.objects.get(user=request.user)
        acc_addr = request.POST['acc_addr']
        from_date = request.POST['from_date']
        to_date = request.POST['to_date']
        if len(to_date):
            to_date = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1)
        else:
            to_date = datetime.now()
        if len(from_date) and not len(acc_addr):
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
            filter_record = set(Transaction.objects.filter(sender=user_acc.acc_id).filter(record_date__range=(from_date, to_date))).union(set(Transaction.objects.filter(recipient=user_acc.acc_id).filter(record_date__range=(from_date, to_date)))) 
        else:
            filter_record = set(Transaction.objects.filter(sender=user_acc.acc_id).filter(record_date__lte=to_date)).union(set(Transaction.objects.filter(recipient=user_acc.acc_id).filter(record_date__lte=to_date))) 
        if Account.objects.filter(acc_id=acc_addr).exists():
            target_acc = Account.objects.get(acc_id=acc_addr)
            at_sender = Transaction.objects.filter(sender=user_acc)
            at_recipient = Transaction.objects.filter(recipient=user_acc)
            filter_at_sender = at_sender.filter(recipient=target_acc)
            filter_at_recipient = at_recipient.filter(sender=target_acc)
            if from_date and to_date:
                filter_at_sender = filter_at_sender.filter(record_date__range=(from_date, to_date))
                filter_at_recipient = filter_at_recipient.filter(record_date__range=(from_date, to_date))
            if not from_date:
                filter_at_sender = filter_at_sender.filter(record_date__lte=to_date)
                filter_at_recipient = filter_at_recipient.filter(record_date__lte=to_date)
            filter_record = set(filter_at_sender).union(set(filter_at_recipient))
        context = {'all_transaction':filter_record, "user":user_acc.acc_id}
        messages.info(request, "Found {} record(s)".format(len(filter_record)))
        return HttpResponse(template.render(context, request))


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
                transaction = Transaction(sender=curr_acc, recipient=rec_acc, amount=amount, remark=remark, complete=True)
                transaction.save()     
                messages.info(request, "You have sent {:.2f} baht to {}".format(amount, rec_acc.user.username))
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
            trans_record.complete=True
            trans_record.save()
            messages.info(request, "You have deposited {:.2f} Baht".format(amount))
            return redirect(request.META['HTTP_REFERER'])
    messages.info(request, "Check the detail again before deposit!")
    return redirect(request.META['HTTP_REFERER'])

def approve_transaction(request, tid):
    if Transaction.objects.filter(id=tid).exists():
       record = Transaction.objects.get(id=tid)
       recipient = record.recipient
       recipient.balance += record.amount
       sender = record.sender
       if sender.balance < record.amount:
           messages.info(request, "Please make sure you have enough balance")
           return redirect(request.META['HTTP_REFERER'])
       sender.balance -= record.amount
       sender.save()
       recipient.save()
       record.complete = True
       record.remark = "Approved at {}".format(timezone.now())
       record.save()
    messages.info(request, "Transaction ID: {} is approved".format(tid))
    return redirect(request.META['HTTP_REFERER'])

def decline_transaction(request, tid):
    if Transaction.objects.filter(id=tid).exists():
        record = Transaction.objects.get(id=tid)
        record.remark = "Transaction is Declined"
        record.complete = True
        record.save()    
    messages.info(request, "Transaction ID: {} is declined".format(tid))
    return redirect(request.META['HTTP_REFERER'])



